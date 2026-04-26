# HW6 — Event-Driven архитектура

**Вариант 13 — Система бронирования отелей**
Брокер: **RabbitMQ** (topic exchange)

## Структура файлов

```
HW/6/
├── event_driven_design.md  # Архитектура, CQRS
├── event_catalog.md        # Каталог событий (payload, producer, consumer)
├── producer.py             # Публикует тестовые события
├── consumer.py             # Принимает события (3 режима очереди)
├── docker-compose.yaml     # RabbitMQ
└── requirements.txt        # pika
```

## Запуск

```bash
# 1. Старт RabbitMQ
docker-compose up -d

# 2. Зависимости
pip install -r requirements.txt

# 3. Запустить consumer (в отдельном терминале)
python consumer.py notifications   # email-уведомления
# или:
python consumer.py analytics       # аналитика
python consumer.py audit_log       # полный аудит

# 4. Опубликовать тестовые события
python producer.py
```

## Пример вывода

**producer.py:**
```
[→] user.registered: {"user_id": "...", "login": "ivan_petrov", ...}
[→] hotel.created:   {"hotel_id": "...", "name": "Marriott Москва", ...}
[→] booking.confirmed: {"booking_id": "...", "total_price": 60000.0, ...}
[→] booking.cancelled: {"booking_id": "...", ...}
[✓] Done
```

**consumer.py notifications:**
```
[*] Listening on queue 'notifications' (bindings: ['booking.confirmed', 'booking.cancelled'])

[←] booking.confirmed at 2026-04-26T10:00:00+00:00
  [notify] Booking abc12345… confirmed — Marriott Москва, 2026-07-01→2026-07-05, 60000.0 ₽ → send email
[←] booking.cancelled at 2026-04-26T10:00:01+00:00
  [notify] Booking abc12345… CANCELLED — Marriott Москва → send cancellation email
```

## Management UI

RabbitMQ Management: http://localhost:15672 (guest / guest)
