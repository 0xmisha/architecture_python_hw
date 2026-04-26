# Event-Driven архитектура — Система бронирования отелей (Вариант 13)
**Федотов Михаил Андреевич М8О-107СВ-25**


## 1. События и команды системы

| Команда (write) | Событие | Инициатор |
|---|---|---|
| RegisterUser | `user.registered` | API — POST /api/auth/register |
| CreateHotel | `hotel.created` | API — POST /api/hotels |
| CreateBooking | `booking.confirmed` | API — POST /api/bookings |
| CancelBooking | `booking.cancelled` | API — DELETE /api/bookings/{id} |

## 2. Компоненты

```
┌──────────────┐   команды    ┌─────────────────┐
│   REST API   │ ──────────►  │  Command Handler │
│  (Producer)  │              │   (PostgreSQL)   │
└──────────────┘              └────────┬────────┘
                                       │ event
                                       ▼
                              ┌─────────────────┐
                              │    RabbitMQ      │
                              │  topic exchange  │
                              │ "hotel_booking"  │
                              └──────┬──────────┘
                    ┌────────────────┼───────────────┐
                    ▼                ▼               ▼
             ┌──────────┐   ┌──────────────┐  ┌──────────┐
             │  Queue:  │   │    Queue:    │  │  Queue:  │
             │ notif-   │   │  analytics   │  │  audit   │
             │ ications │   │              │  │   log    │
             └──────────┘   └──────────────┘  └──────────┘
             Email/SMS       Статистика         Аудит
             Consumer        Consumer           Consumer
```

## 3. Брокер: RabbitMQ

**Тип exchange:** `topic` — позволяет подписываться по маске (`booking.*`, `#`).

| Exchange | Тип | Routing key | Queue | Потребитель |
|---|---|---|---|---|
| `hotel_booking` | topic | `user.*` | `analytics` | Сервис аналитики |
| `hotel_booking` | topic | `hotel.*` | `analytics` | Сервис аналитики |
| `hotel_booking` | topic | `booking.confirmed` | `notifications` | Email-сервис |
| `hotel_booking` | topic | `booking.cancelled` | `notifications` | Email-сервис |
| `hotel_booking` | topic | `booking.*` | `analytics` | Сервис аналитики |
| `hotel_booking` | topic | `#` | `audit_log` | Аудит |

**Гарантии доставки:** `at-least-once`
- Publisher confirms (`mandatory=True`) — брокер подтверждает прием
- Consumer manual ack — сообщение не удаляется до успешной обработки
- Durable queues + persistent messages — переживают перезапуск брокера

## 4. CQRS

Паттерн применим: разделение на команды (write) и запросы (read).

```
Commands (write side):          Queries (read side):
  CreateBooking ──► DB write      ListHotels   ──► PostgreSQL / Redis cache
  CancelBooking ──► DB update     SearchHotels ──► Redis cache (HW5)
  CreateHotel   ──► DB write      GetBookings  ──► PostgreSQL read replica
                         │
                         └──► событие ──► синхронизация read-модели
                                          (инвалидация кэша, обновление replica)
```

При создании отеля (`hotel.created`) consumer инвалидирует Redis-кэш (`hotels:list`, `hotels:city:*`) — то же, что делает HW5, но через событие, а не inline.
