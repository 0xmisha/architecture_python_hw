# HW4 — Проектирование и работа с MongoDB

**Вариант 13 — Система бронирования отелей** (аналог [booking.com](https://www.booking.com/))

## Документная модель

Три коллекции: **users**, **hotels**, **bookings**.

Ключевые решения по embedded/references — см. [schema_design.md](schema_design.md).

### Структура документа booking (ключевой пример)

```json
{
  "_id": ObjectId,
  "user_id":  ObjectId,
  "hotel_id": ObjectId,
  "hotel_snapshot": {
    "name":            "Marriott Москва",
    "city":            "Москва",
    "price_per_night": 15000.0
  },
  "check_in":    ISODate,
  "check_out":   ISODate,
  "nights":      5,
  "total_price": 75000.0,
  "status":      "confirmed",
  "created_at":  ISODate
}
```

`hotel_snapshot` — денормализация: имя/город отеля хранятся в бронировании, чтобы не делать `$lookup` при каждом запросе списка броней.

## Структура файлов

```
HW/4/
├── app/
│   ├── main.py          # FastAPI + lifespan
│   ├── database.py      # PyMongo подключение + индексы
│   ├── schemas.py       # Pydantic схемы
│   ├── auth.py          # JWT-аутентификация
│   └── routers/
│       ├── auth.py      # POST /api/auth/register, /login
│       ├── users.py     # GET  /api/users/search, /{id}
│       ├── hotels.py    # CRUD /api/hotels
│       └── bookings.py  # CRUD /api/bookings
├── schema_design.md     # Проектирование: embedded vs references
├── data.js              # Тестовые данные (mongosh-скрипт)
├── queries.js           # MongoDB-запросы для всех операций
├── validation.js        # $jsonSchema валидация + тесты
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
# Запуск MongoDB + API
docker-compose up --build

# API: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

### Ручной запуск (без Docker)

```bash
# 1. Запустить MongoDB
docker run -d -p 27017:27017 --name mongo mongo:7.0

# 2. Загрузить данные
mongosh hotel_booking data.js

# 3. Настроить валидацию (опционально)
mongosh hotel_booking validation.js

# 4. Запустить API
pip install -r requirements.txt
MONGO_URL=mongodb://localhost:27017 uvicorn app.main:app --reload
```

### Выполнение MongoDB-запросов

```bash
# Подключиться к mongosh
docker exec -it hw4-mongodb-1 mongosh hotel_booking

# Загрузить запросы
load("queries.js")
```

## Тестирование

```bash
# Регистрация
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"login":"test","password":"pass1","first_name":"Test","last_name":"User","email":"t@t.com"}'

# Логин
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"test","password":"pass1"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Поиск отелей по городу
curl "http://localhost:8000/api/hotels/search?city=Москва"

# Создание бронирования
curl -X POST http://localhost:8000/api/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"hotel_id":"<id>","check_in":"2026-07-01","check_out":"2026-07-05"}'
```
