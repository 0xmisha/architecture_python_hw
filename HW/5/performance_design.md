# Проектирование производительности
**Федотов Михаил Андреевич М8О-107СВ-25**

## Система бронирования отелей (Вариант 13)

---

## 1. Анализ горячих путей (Hot Paths)

### Частые операции (высокая нагрузка)

| Endpoint | Частота | Причина |
|---|---|---|
| `GET /api/hotels` | Очень высокая | Главная страница, все посетители |
| `GET /api/hotels/search?city=` | Очень высокая | Основной UX-поток поиска |
| `GET /api/hotels/{id}` | Высокая | Страница конкретного отеля |
| `POST /api/auth/login` | Средняя | Каждая сессия |
| `GET /api/bookings/my` | Средняя | Личный кабинет |

### Медленные операции

| Операция | Ожидаемое время | Причина |
|---|---|---|
| `SELECT * FROM hotels ORDER BY city` | 10–50 мс | Полный скан при отсутствии кэша |
| `SELECT ... WHERE city ILIKE '%X%'` | 5–20 мс | GIN-индекс ускоряет, но всё равно I/O |
| JOIN bookings + hotels | 15–40 мс | Два I/O на разные таблицы |
| `POST /api/auth/register` (bcrypt) | 80–200 мс | Намеренно медленный хэш пароля |

### Требования к про��зводительности

| Метрика | Цель |
|---|---|
| P50 (list hotels) | < 5 мс (с кэшем) |
| P99 (list hotels) | < 50 мс |
| P50 (search by city) | < 5 мс (с кэшем) |
| Cache hit rate | ≥ 80 % для hotel-эндпоинтов |
| Rate limit (register) | 5 req / мин / IP |
| Rate limit (search) | 30 req / мин / IP |
| Rate limit (booking) | 10 req / мин / IP |

---

## 2. Стратегия кэширования

### Что кэшируем и почему

| Данные | Ключ кэша | Стратегия | TTL | Обоснование |
|---|---|---|---|---|
| Список всех отелей | `hotels:list` | Cache-Aside | 300 с | Редко меняется, читается очень часто |
| Поиск отелей по городу | `hotels:city:{city}` | Cache-Aside | 300 с | Повторяющиеся запросы (Москва, СПб) |
| Отель по ID | `hotels:one:{id}` | Cache-Aside | 300 с | Детальная страница отеля |

### Что НЕ кэшируем

| Данные | Причина |
|---|---|
| Бронирования пользователя | Персональные, часто меняются, не shared |
| Данные конкретного пользователя | Персональные, безопасность |
| Результат `POST`-запросов | Мутирующие операции |

### Стратегия Cache-Aside (Lazy Loading)

```
Client → API → Cache HIT? → return cached
                  ↓ MISS
               DB query → store in cache → return result
```

**Почему Cache-Aside, а не Read-Through:**
- Полный контроль над ключами и TTL в коде
- Можно явно инвалидировать при записи
- Простота реализации без дополнительного промежуточного слоя

### Инвалидация кэша

| Триггер | Инвалидируемые ключи |
|---|---|
| `POST /api/hotels` (создание отеля) | `hotels:list`, `hotels:city:*` |
| `GET /api/hotels/{id}` (промах) | обновляет `hotels:one:{id}` |

При создании отеля удаляем `hotels:list` и все `hotels:city:*` через `SCAN` + `DEL`. Отдельные ключи `hotels:one:{id}` не инвалидируем при создании нового отеля — они сами истекут по TTL.

---

## 3. Стратегия Rate Limiting

### Выбранный алгоритм: Sliding Window Counter (Redis ZSET)

**Почему Sliding Window, а не Fixed Window:**
- Fixed Window допускает "burst" на стыке окон: 100 запросов в конце первой минуты + 100 в начале второй = 200 за 2 секунды.
- Sliding Window равномерно размазывает нагрузку.
- Redis ZSET с `ZADD` / `ZREMRANGEBYSCORE` / `ZCARD` — O(log N) на операцию.

```
Key: rl:{prefix}:{client_ip}
Members: time.time_ns() (уникальный timestamp в нс)
Score: time.time()   (float-секунды для range-запросов)

При каждом запросе:
  1. ZREMRANGEBYSCORE key 0 (now - window)   — удалить устаревшие
  2. ZADD key {ns_timestamp: now}             — добавить текущий
  3. ZCARD key                                — получить счётчик
  4. EXPIRE key window+1                      — автоочистка
```

### Лимиты по эндпоинтам

| Endpoint | Ключ | Лимит | Окно | Алгоритм | Обоснование |
|---|---|---|---|---|---|
| `POST /api/auth/register` | IP | 5 | 60 с | Sliding Window | Защита от массовой регистрации |
| `GET /api/hotels/search` | IP | 30 | 60 с | Sliding Window | Защита от скрапинга |
| `POST /api/bookings` | IP | 10 | 60 с | Sliding Window | Защита от спама бронирований |

### HTTP-заголовки ответа

Каждый ответ (включая 429) содержит:

```
X-RateLimit-Limit:     <максимум запросов в окне>
X-RateLimit-Remaining: <осталось в текущем окне>
X-RateLimit-Reset:     <Unix timestamp конца окна>
Retry-After:           <секунд до сброса> (только при 429)
```

---

## 4. Влияние на производительность

### Кэширование

| Сценарий | Без кэша | С кэшем | Улучшение |
|---|---|---|---|
| `GET /api/hotels` (100 отелей в БД) | ~30 мс | ~1 мс | 30× |
| `GET /api/hotels/search?city=Москва` | ~20 мс | ~1 мс | 20× |
| `GET /api/hotels/{id}` | ~10 мс | <1 мс | 15× |
| Нагрузка на PostgreSQL при 1000 RPS | 1000 запросов/с | ~200 запросов/с (80% hit rate) | −80% |

### Rate Limiting

| Эффект | Описание |
|---|---|
| DDoS-защита | Атака на `/register` ограничена 5 req/мин/IP |
| Защита от скрапинга | Автоматический сбор данных отелей замедлен |
| Стабильность | Равномерная нагрузка на БД и кэш |
| SLA | Легитимные пользователи получают предсказуемое время ответа |

---

## 5. Метрики мониторинга

| Метрика | Как измерить | Целевое значение |
|---|---|---|
| Cache hit rate | `redis INFO stats` → `keyspace_hits / (hits + misses)` | ≥ 80 % |
| P50/P95/P99 latency | Prometheus `histogram_quantile` | < 5 / 20 / 50 мс |
| Rate limit hits (429/с) | счётчик в Prometheus | < 1 % от общего трафика |
| Redis memory usage | `redis INFO memory` → `used_memory_human` | < 100 МБ |
| DB connections | SQLAlchemy pool metrics | < 90 % от pool size |

### Формула Cache Hit Rate

```
hit_rate = keyspace_hits / (keyspace_hits + keyspace_misses) * 100%
```

Дополнительно: в логах API можно добавить заголовок `X-Cache: HIT|MISS` для отладки.
