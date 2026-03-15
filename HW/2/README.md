# Домашнее задание 02: REST API — Система бронирования отелей

**Вариант 13** — Система бронирования отелей (Booking.com)

## Описание

REST API сервис для бронирования отелей, реализованный на Python FastAPI.

### Сущности

- **Пользователь** — регистрация, аутентификация, поиск
- **Отель** — создание, просмотр, поиск по городу
- **Бронирование** — создание, просмотр, отмена

### Стек технологий

- Python 3.12 + FastAPI
- JWT аутентификация (python-jose + passlib/bcrypt)
- In-memory хранилище (dict)
- Pydantic DTO
- pytest для тестирования

## Запуск

### Docker

```bash
docker compose up --build
```

API доступно по адресу: http://localhost:8000

### Локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Swagger UI

После запуска доступен по адресу: http://localhost:8000/docs

OpenAPI спецификация также находится в файле `openapi.yaml`.

## API Endpoints

### Auth

| Метод | URL | Описание | Аутентификация |
|-------|-----|----------|----------------|
| POST | `/api/auth/register` | Регистрация пользователя | Нет |
| POST | `/api/auth/login` | Логин, получение JWT токена | Нет |

### Users

| Метод | URL | Описание | Аутентификация |
|-------|-----|----------|----------------|
| GET | `/api/users/search?login=...` | Поиск по логину | JWT |
| GET | `/api/users/search?name=...` | Поиск по маске имя/фамилии | JWT |
| GET | `/api/users/{user_id}` | Получение пользователя по ID | JWT |

### Hotels

| Метод | URL | Описание | Аутентификация |
|-------|-----|----------|----------------|
| POST | `/api/hotels` | Создание отеля | JWT |
| GET | `/api/hotels` | Список всех отелей | Нет |
| GET | `/api/hotels/search?city=...` | Поиск отелей по городу | Нет |
| GET | `/api/hotels/{hotel_id}` | Получение отеля по ID | Нет |

### Bookings

| Метод | URL | Описание | Аутентификация |
|-------|-----|----------|----------------|
| POST | `/api/bookings` | Создание бронирования | JWT |
| GET | `/api/bookings/my` | Бронирования текущего пользователя | JWT |
| GET | `/api/bookings/{booking_id}` | Получение бронирования по ID | JWT |
| DELETE | `/api/bookings/{booking_id}` | Отмена бронирования | JWT |

## Примеры использования

### Регистрация

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"login":"ivan","password":"pass1234","first_name":"Ivan","last_name":"Petrov","email":"ivan@example.com"}'
```

### Логин

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"ivan","password":"pass1234"}'
```

### Создание отеля (с токеном)

```bash
curl -X POST http://localhost:8000/api/hotels \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"name":"Grand Hotel","city":"Moscow","address":"Tverskaya 1","stars":5,"rooms_total":100,"price_per_night":5000}'
```

### Создание бронирования

```bash
curl -X POST http://localhost:8000/api/bookings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"hotel_id":"<HOTEL_ID>","check_in":"2026-06-01","check_out":"2026-06-05"}'
```

### Отмена бронирования

```bash
curl -X DELETE http://localhost:8000/api/bookings/<BOOKING_ID> \
  -H "Authorization: Bearer <TOKEN>"
```

## Тестирование

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

20 тестов покрывают все endpoints: успешные сценарии, ошибки валидации, авторизацию и обработку несуществующих ресурсов.

## Структура проекта

```
HW/2/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI приложение
│   ├── auth.py            # JWT аутентификация
│   ├── database.py        # In-memory хранилище
│   ├── schemas.py         # Pydantic DTO
│   └── routers/
│       ├── __init__.py
│       ├── auth.py        # /api/auth/*
│       ├── users.py       # /api/users/*
│       ├── hotels.py      # /api/hotels/*
│       └── bookings.py    # /api/bookings/*
├── tests/
│   ├── __init__.py
│   └── test_api.py        # 20 тестов
├── openapi.yaml           # OpenAPI 3.0 спецификация
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── README.md
```
