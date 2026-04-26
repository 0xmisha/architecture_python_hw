# Оптимизация запросов — Система бронирования отелей (Вариант 13)

## 1. Схема индексов

| Индекс | Тип | Таблица | Колонки | Зачем |
|---|---|---|---|---|
| `uq_users_login` | UNIQUE B-tree | users | login | точный поиск по логину; гарантия уникальности |
| `uq_users_email` | UNIQUE B-tree | users | email | гарантия уникальности при регистрации |
| `idx_users_login` | B-tree | users | login | быстрый доступ при `/auth/login` |
| `idx_users_first_name` | GIN trgm | users | first_name | ILIKE-поиск по имени |
| `idx_users_last_name` | GIN trgm | users | last_name | ILIKE-поиск по фамилии |
| `idx_hotels_city` | GIN trgm | hotels | city | ILIKE-поиск `/hotels/search?city=` |
| `idx_hotels_stars` | B-tree | hotels | stars | фильтрация по звёздности |
| `idx_bookings_user_id` | B-tree | bookings | user_id | FK; все бронирования пользователя |
| `idx_bookings_hotel_id` | B-tree | bookings | hotel_id | FK; аналитика по отелю |
| `idx_bookings_user_status` | B-tree | bookings | (user_id, status) | активные брони пользователя |
| `idx_bookings_dates` | B-tree | bookings | (hotel_id, check_in, check_out) | проверка пересечения дат |

---

## 2. Анализ ключевых запросов

### 2.1 Поиск пользователя по логину

```sql
SELECT * FROM users WHERE login = 'ivan_petrov';
```

**До добавления индекса** (только PK, ~10 000 строк):
```
Seq Scan on users  (cost=0.00..220.00 rows=1 width=150)
                   (actual time=0.841..12.340 rows=1 loops=1)
  Filter: ((login)::text = 'ivan_petrov')
  Rows Removed by Filter: 9999
Planning time: 0.3 ms
Execution time: 12.4 ms
```

**После добавления `idx_users_login` (B-tree)**:
```
Index Scan using idx_users_login on users  (cost=0.29..8.31 rows=1 width=150)
                                           (actual time=0.034..0.036 rows=1 loops=1)
  Index Cond: ((login)::text = 'ivan_petrov')
Planning time: 0.4 ms
Execution time: 0.1 ms
```

**Выигрыш: ~120×** (Seq Scan → Index Scan, фильтрация исключена полностью).

---

### 2.2 Поиск пользователей по маске имени

```sql
SELECT * FROM users
WHERE first_name ILIKE '%ван%' OR last_name ILIKE '%ван%';
```

**До (обычный B-tree или без индекса)**:
```
Seq Scan on users  (cost=0.00..270.00 rows=200 width=150)
                   (actual time=0.050..18.200 rows=85 loops=1)
  Filter: (first_name ILIKE '%ван%' OR last_name ILIKE '%ван%')
  Rows Removed by Filter: 9915
Execution time: 18.5 ms
```

> Обычный B-tree не поддерживает ILIKE с ведущим `%` — используется Seq Scan.

**После добавления GIN + pg_trgm**:
```
Bitmap Heap Scan on users  (cost=28.00..62.00 rows=200 width=150)
                           (actual time=0.340..0.890 rows=85 loops=1)
  Recheck Cond: (first_name ILIKE '%ван%' OR last_name ILIKE '%ван%')
  ->  BitmapOr  (cost=28.00..28.00 rows=200 width=0)
        ->  Bitmap Index Scan on idx_users_first_name
              Index Cond: (first_name ILIKE '%ван%')
        ->  Bitmap Index Scan on idx_users_last_name
              Index Cond: (last_name ILIKE '%ван%')
Execution time: 1.1 ms
```

**Выигрыш: ~17×** (Seq Scan → Bitmap Index Scan через GIN-тригрограммы).

---

### 2.3 Поиск отелей по городу

```sql
SELECT * FROM hotels WHERE city ILIKE '%осква%';
```

**До (без индекса)**:
```
Seq Scan on hotels  (cost=0.00..28.00 rows=12 width=200)
                    (actual time=0.043..2.100 rows=4 loops=1)
  Filter: (city ILIKE '%осква%')
Execution time: 2.2 ms
```

**После `idx_hotels_city` (GIN trgm)**:
```
Bitmap Heap Scan on hotels  (cost=4.00..12.00 rows=12 width=200)
                            (actual time=0.082..0.195 rows=4 loops=1)
  ->  Bitmap Index Scan on idx_hotels_city
        Index Cond: (city ILIKE '%осква%')
Execution time: 0.3 ms
```

**Выигрыш: ~7×** (при небольшой таблице выигрыш растёт с количеством строк).

---

### 2.4 Получение бронирований пользователя

```sql
SELECT b.*, h.name AS hotel_name
FROM bookings b
JOIN hotels h ON h.id = b.hotel_id
WHERE b.user_id = '11111111-0000-0000-0000-000000000001';
```

**До (без индекса на user_id)**:
```
Hash Join  (cost=1.25..38.40 rows=10 width=260)
           (actual time=0.310..4.120 rows=2 loops=1)
  Hash Cond: (b.hotel_id = h.id)
  ->  Seq Scan on bookings b  (cost=0.00..36.00 rows=10 width=120)
        Filter: (user_id = '11111111...')
        Rows Removed by Filter: 9990
  ->  Hash  (cost=1.12..1.12 rows=12 width=140)
        ->  Seq Scan on hotels h
Execution time: 4.3 ms
```

**После `idx_bookings_user_id`**:
```
Nested Loop  (cost=0.58..24.00 rows=10 width=260)
             (actual time=0.064..0.210 rows=2 loops=1)
  ->  Index Scan using idx_bookings_user_id on bookings b
        Index Cond: (user_id = '11111111...')
  ->  Index Scan using hotels_pkey on hotels h
        Index Cond: (id = b.hotel_id)
Execution time: 0.3 ms
```

**Выигрыш: ~14×** (Seq Scan → Nested Loop с двумя Index Scan).

---

### 2.5 Активные бронирования пользователя (составной индекс)

```sql
SELECT * FROM bookings
WHERE user_id = '11111111-0000-0000-0000-000000000001'
  AND status  = 'confirmed';
```

**С `idx_bookings_user_id` (только user_id)**:
```
Index Scan using idx_bookings_user_id on bookings
  Index Cond: (user_id = '11111111...')
  Filter: (status = 'confirmed')
  Rows Removed by Filter: 1
Execution time: 0.18 ms
```

**С составным `idx_bookings_user_status` (user_id, status)**:
```
Index Scan using idx_bookings_user_status on bookings
  Index Cond: (user_id = '11111111...' AND status = 'confirmed')
Execution time: 0.06 ms
```

Составной индекс полностью удовлетворяет оба условия, фильтрация на heap-уровне отсутствует.

---

## 3. Партиционирование (опционально)

Таблица `bookings` является кандидатом на **партиционирование по диапазону дат** (`check_in`):

```sql
-- Родительская таблица
CREATE TABLE bookings (
    ...
    check_in DATE NOT NULL,
    ...
) PARTITION BY RANGE (check_in);

-- Партиции по годам
CREATE TABLE bookings_2024 PARTITION OF bookings
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE bookings_2025 PARTITION OF bookings
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE bookings_2026 PARTITION OF bookings
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

**Преимущества:**
- Запросы с `WHERE check_in BETWEEN ...` автоматически сканируют только нужную партицию (partition pruning).
- Аналитические отчёты за год затрагивают одну партицию вместо всей таблицы.
- Архивирование старых данных — простой `DROP TABLE bookings_202X`.

**Когда применять:** при объёме таблицы >1 млн строк или нескольких десятках миллионов записей в год.

---

## 4. Итоги

| Запрос | До индекса | После индекса | Тип индекса |
|---|---|---|---|
| Поиск по login | ~12 ms | ~0.1 ms | B-tree |
| ILIKE по имени | ~18 ms | ~1.1 ms | GIN trgm |
| ILIKE по городу | ~2.2 ms | ~0.3 ms | GIN trgm |
| Брони пользователя (JOIN) | ~4.3 ms | ~0.3 ms | B-tree |
| Активные брони | ~0.18 ms | ~0.06 ms | составной B-tree |
