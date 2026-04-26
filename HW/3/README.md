# HW3 — Проектирование и оптимизация реляционной БД
**Федотов Михаил Андреевич М8О-107СВ-25**


**Вариант 13 — Система бронирования отелей** (аналог [booking.com](https://www.booking.com/))

## Схема базы данных

### Сущности

| Таблица | Описание |
|---|---|
| `users` | Пользователи системы |
| `hotels` | Отели |
| `bookings` | Бронирования |

### ER-диаграмма

```
users ──< bookings >── hotels
```

### Таблица `users`

| Колонка | Тип | Ограничения |
|---|---|---|
| id | UUID | PK, DEFAULT gen_random_uuid() |
| login | VARCHAR(50) | NOT NULL, UNIQUE |
| password_hash | VARCHAR(255) | NOT NULL |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | NOT NULL, UNIQUE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

### Таблица `hotels`

| Колонка | Тип | Ограничения |
|---|---|---|
| id | UUID | PK, DEFAULT gen_random_uuid() |
| name | VARCHAR(255) | NOT NULL |
| city | VARCHAR(100) | NOT NULL |
| address | VARCHAR(500) | NOT NULL |
| stars | SMALLINT | NOT NULL, CHECK 1–5 |
| rooms_total | INTEGER | NOT NULL, CHECK > 0 |
| price_per_night | NUMERIC(12,2) | NOT NULL, CHECK > 0 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

### Таблица `bookings`

| Колонка | Тип | Ограничения |
|---|---|---|
| id | UUID | PK, DEFAULT gen_random_uuid() |
| user_id | UUID | NOT NULL, FK → users(id) |
| hotel_id | UUID | NOT NULL, FK → hotels(id) |
| check_in | DATE | NOT NULL |
| check_out | DATE | NOT NULL, CHECK > check_in |
| total_price | NUMERIC(12,2) | NOT NULL, CHECK >= 0 |
| status | VARCHAR(20) | NOT NULL, CHECK IN ('confirmed','cancelled') |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

## Индексы

| Индекс | Тип | Обоснование |
|---|---|---|
| `uq_users_login` | UNIQUE B-tree | Гарантия уникальности логина |
| `idx_users_login` | B-tree | Быстрый поиск при логине |
| `idx_users_first_name` | GIN trgm | ILIKE-поиск по имени |
| `idx_users_last_name` | GIN trgm | ILIKE-поиск по фамилии |
| `idx_hotels_city` | GIN trgm | ILIKE-поиск отелей по городу |
| `idx_hotels_stars` | B-tree | Фильтрация по звёздности |
| `idx_bookings_user_id` | B-tree | Все брони пользователя |
| `idx_bookings_hotel_id` | B-tree | Аналитика по отелю |
| `idx_bookings_user_status` | B-tree (составной) | Активные брони пользователя |
| `idx_bookings_dates` | B-tree (составной) | Проверка пересечения дат |

## Структура файлов

```
HW/3/
├── app/
│   ├── main.py          # FastAPI приложение
│   ├── database.py      # SQLAlchemy engine + session
│   ├── models.py        # ORM-модели
│   ├── schemas.py       # Pydantic-схемы
│   ├── auth.py          # JWT-аутентификация
│   └── routers/
│       ├── auth.py      # POST /api/auth/register, /login
│       ├── users.py     # GET  /api/users/search, /{id}
│       ├── hotels.py    # CRUD /api/hotels
│       └── bookings.py  # CRUD /api/bookings
├── schema.sql           # DDL: CREATE TABLE + индексы
├── data.sql             # DML: тестовые данные
├── queries.sql          # Все API-запросы в виде SQL
├── optimization.md      # Анализ планов EXPLAIN + оптимизации
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt
```

## API

| Метод | Эндпоинт | Авторизация | Описание |
|---|---|---|---|
| POST | /api/auth/register | — | Создание нового пользователя |
| POST | /api/auth/login | — | Получение JWT-токена |
| GET | /api/users/search?login= | JWT | Поиск пользователя по логину |
| GET | /api/users/search?name= | JWT | Поиск по маске имени/фамилии |
| GET | /api/users/{id} | JWT | Получение пользователя по ID |
| POST | /api/hotels | JWT | Создание отеля |
| GET | /api/hotels | — | Список всех отелей |
| GET | /api/hotels/search?city= | — | Поиск отелей по городу |
| GET | /api/hotels/{id} | — | Получение отеля по ID |
| POST | /api/bookings | JWT | Создание бронирования |
| GET | /api/bookings/my | JWT | Бронирования текущего пользователя |
| GET | /api/bookings/{id} | JWT | Получение бронирования по ID |
| DELETE | /api/bookings/{id} | JWT | Отмена бронирования |

## Запуск

```bash
# Запуск PostgreSQL + API
docker-compose up --build

# API доступно на http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### Ручной запуск (без Docker)

```bash
# 1. Создать базу данных
psql -U postgres -c "CREATE DATABASE hotel_booking;"
psql -U postgres -d hotel_booking -f schema.sql
psql -U postgres -d hotel_booking -f data.sql

# 2. Запустить API
pip install -r requirements.txt
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hotel_booking \
    uvicorn app.main:app --reload
```

## Тестирование

```bash
# Регистрация
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"login":"test","password":"pass1","first_name":"Test","last_name":"User","email":"t@t.com"}'

# Логин
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"test","password":"pass1"}'

# Поиск отелей по городу
curl "http://localhost:8000/api/hotels/search?city=Москва"
```
