# HW3 — Реляционная БД для системы бронирования отелей
**Федотов Михаил Андреевич М8О-107СВ-25**

Вариант 13, booking.com-подобная система.

## Про схему

Три таблицы: пользователи, отели, бронирования. Связи очевидные — бронирование ссылается на обе остальные через FK.

```
users ──< bookings >── hotels
```

### users

| Колонка | Тип | Примечания |
|---|---|---|
| id | UUID | gen_random_uuid() |
| login | VARCHAR(50) | уникальный |
| password_hash | VARCHAR(255) | bcrypt |
| first_name | VARCHAR(100) | |
| last_name | VARCHAR(100) | |
| email | VARCHAR(255) | уникальный |
| created_at | TIMESTAMPTZ | |

### hotels

| Колонка | Тип | Примечания |
|---|---|---|
| id | UUID | |
| name | VARCHAR(255) | |
| city | VARCHAR(100) | |
| address | VARCHAR(500) | |
| stars | SMALLINT | CHECK 1–5 |
| rooms_total | INTEGER | CHECK > 0 |
| price_per_night | NUMERIC(12,2) | CHECK > 0 |
| created_at | TIMESTAMPTZ | |

### bookings

| Колонка | Тип | Примечания |
|---|---|---|
| id | UUID | |
| user_id | UUID | FK → users |
| hotel_id | UUID | FK → hotels |
| check_in | DATE | |
| check_out | DATE | CHECK > check_in |
| total_price | NUMERIC(12,2) | считается при создании |
| status | VARCHAR(20) | confirmed / cancelled |
| created_at | TIMESTAMPTZ | |

## Про индексы

Самое интересное в этом задании. Сначала поставил просто B-tree на всё подряд, потом понял что ILIKE '%москва%' с ведущим процентом по B-tree вообще не работает — нужен GIN + расширение pg_trgm. Поэтому для поиска по имени и городу именно GIN.

Составной индекс `(user_id, status)` на bookings — чтобы не фильтровать по статусу после выборки по пользователю. Без него postgres делал index scan по user_id а потом ещё фильтровал строки в памяти.

| Индекс | Тип | Зачем |
|---|---|---|
| uq_users_login | UNIQUE B-tree | уникальность + поиск при логине |
| idx_users_first_name | GIN trgm | ILIKE поиск по имени |
| idx_users_last_name | GIN trgm | ILIKE поиск по фамилии |
| idx_hotels_city | GIN trgm | ILIKE поиск по городу |
| idx_hotels_stars | B-tree | фильтр по звёздам |
| idx_bookings_user_id | B-tree | все брони пользователя |
| idx_bookings_hotel_id | B-tree | нужен для FK constraint и аналитики |
| idx_bookings_user_status | B-tree составной | активные брони без лишней фильтрации |
| idx_bookings_dates | B-tree составной | проверка пересечения дат при бронировании |

## Файлы

- `schema.sql` — CREATE TABLE + все индексы
- `data.sql` — тестовые данные (10+ записей в каждой таблице)
- `queries.sql` — SQL для всех операций из варианта
- `optimization.md` — EXPLAIN до/после, там подробнее про конкретные планы

Само API в папке `app/`, структура та же что в HW2 только база данных теперь реальная через SQLAlchemy, а не словари в памяти.

## Запуск

```bash
docker-compose up --build
```

Поднимает postgres и api вместе. API на http://localhost:8000, swagger на /docs.

Если хочется без докера:

```bash
psql -U postgres -c "CREATE DATABASE hotel_booking;"
psql -U postgres -d hotel_booking -f schema.sql
psql -U postgres -d hotel_booking -f data.sql

pip install -r requirements.txt
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hotel_booking uvicorn app.main:app --reload
```

## Эндпоинты

| Метод | Путь | Auth | Что делает |
|---|---|---|---|
| POST | /api/auth/register | — | регистрация |
| POST | /api/auth/login | — | логин, возвращает JWT |
| GET | /api/users/search?login= | JWT | поиск по логину |
| GET | /api/users/search?name= | JWT | поиск по маске имени/фамилии |
| POST | /api/hotels | JWT | создать отель |
| GET | /api/hotels | — | список всех |
| GET | /api/hotels/search?city= | — | поиск по городу |
| POST | /api/bookings | JWT | создать бронирование |
| GET | /api/bookings/my | JWT | мои брони |
| DELETE | /api/bookings/{id} | JWT | отмена |
