# HW5 — Кэширование и Rate Limiting
**Федотов Михаил Андреевич М8О-107СВ-25**


**Вариант 13 — Система бронирования отелей**

Расширение HW3 (PostgreSQL + SQLAlchemy): добавлены **Redis-кэш** и **rate limiting**.

## Что реализовано

### Кэширование (Redis, Cache-Aside)

| Endpoint | Ключ Redis | TTL | Инвалидация |
|---|---|---|---|
| `GET /api/hotels` | `hotels:list` | 300 с | при `POST /api/hotels` |
| `GET /api/hotels/search?city=` | `hotels:city:{city}` | 300 с | при `POST /api/hotels` |
| `GET /api/hotels/{id}` | `hotels:one:{id}` | 300 с | по TTL |

Ответ содержит заголовок `X-Cache: HIT` или `X-Cache: MISS`.

### Rate Limiting (Sliding Window Counter, Redis ZSET)

| Endpoint | Лимит | Окно | Алгоритм |
|---|---|---|---|
| `POST /api/auth/register` | 5 req / IP | 60 с | Sliding Window |
| `GET /api/hotels/search` | 30 req / IP | 60 с | Sliding Window |
| `POST /api/bookings` | 10 req / IP | 60 с | Sliding Window |

При превышении лимита возвращается `429 Too Many Requests`.

Все ответы (включая 429) содержат заголовки:
```
X-RateLimit-Limit:     <лимит>
X-RateLimit-Remaining: <осталось>
X-RateLimit-Reset:     <unix timestamp сброса>
Retry-After:           <секунд до сброса>  # только при 429
```

## Структура файлов

```
HW/5/
├── app/
│   ├── cache.py        # Redis cache helper (get/set/delete/delete_pattern)
│   ├── rate_limit.py   # Sliding Window rate limiter (FastAPI dependency factory)
│   ├── main.py
│   ├── database.py     # SQLAlchemy (PostgreSQL)
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── routers/
│       ├── auth.py     # + rate limit на /register
│       ├── hotels.py   # + кэш на GET, + rate limit на /search
│       ├── bookings.py # + rate limit на POST
│       └── users.py
├── performance_design.md  # Анализ производительности
├── Dockerfile
├── docker-compose.yaml    # PostgreSQL + Redis + API
└── requirements.txt
```

## Запуск

```bash
docker-compose up --build
# API: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

## Проверка кэша

```bash
# Первый запрос — MISS, загружает из БД и кэширует
curl -v http://localhost:8000/api/hotels 2>&1 | grep "X-Cache"
# X-Cache: MISS

# Второй запрос — HIT, из Redis
curl -v http://localhost:8000/api/hotels 2>&1 | grep "X-Cache"
# X-Cache: HIT

# Мониторинг через Redis CLI
docker exec -it hw5-redis-1 redis-cli
> INFO stats           # keyspace_hits, keyspace_misses
> KEYS hotels:*        # просмотр кэш-ключей
> TTL hotels:list      # оставшийся TTL
```

## Проверка Rate Limiting

```bash
# Попытаться зарегистрироваться 6 раз подряд (лимит 5/мин)
for i in {1..6}; do
  curl -s -o /dev/null -w "%{http_code} " -X POST http://localhost:8000/api/auth/register \
    -H "Content-Type: application/json" \
    -d "{\"login\":\"user$i\",\"password\":\"pass1\",\"first_name\":\"A\",\"last_name\":\"B\",\"email\":\"u$i@t.com\"}"
done
# Ожидаемый вывод: 201 201 201 201 201 429

# Проверить заголовки rate limit
curl -v -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"login":"rl_test","password":"pass1","first_name":"A","last_name":"B","email":"rl@t.com"}' \
  2>&1 | grep -i "x-ratelimit"
# X-RateLimit-Limit: 5
# X-RateLimit-Remaining: 4
# X-RateLimit-Reset: 1746...
```
