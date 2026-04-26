# Каталог событий — Система бронирования отелей (Вариант 13)
**Федотов Михаил Андреевич М8О-107СВ-25**


---

## user.registered

| Поле | Значение |
|---|---|
| **Exchange** | `hotel_booking` (topic) |
| **Routing key** | `user.registered` |
| **Producer** | API: POST /api/auth/register |
| **Consumers** | `analytics` |
| **Гарантии** | at-least-once |

**Payload:**
```json
{
  "event":      "user.registered",
  "occurred_at":"2026-04-26T10:00:00Z",
  "payload": {
    "user_id":    "uuid",
    "login":      "ivan_petrov",
    "email":      "ivan@mail.ru"
  }
}
```

---

## hotel.created

| Поле | Значение |
|---|---|
| **Exchange** | `hotel_booking` (topic) |
| **Routing key** | `hotel.created` |
| **Producer** | API: POST /api/hotels |
| **Consumers** | `analytics`, `audit_log` |
| **Гарантии** | at-least-once |

**Payload:**
```json
{
  "event":      "hotel.created",
  "occurred_at":"2026-04-26T10:05:00Z",
  "payload": {
    "hotel_id":        "uuid",
    "name":            "Marriott Москва",
    "city":            "Москва",
    "stars":           5,
    "price_per_night": 15000.0
  }
}
```

---

## booking.confirmed

| Поле | Значение |
|---|---|
| **Exchange** | `hotel_booking` (topic) |
| **Routing key** | `booking.confirmed` |
| **Producer** | API: POST /api/bookings |
| **Consumers** | `notifications`, `analytics`, `audit_log` |
| **Гарантии** | at-least-once |

**Payload:**
```json
{
  "event":      "booking.confirmed",
  "occurred_at":"2026-04-26T11:00:00Z",
  "payload": {
    "booking_id":  "uuid",
    "user_id":     "uuid",
    "hotel_id":    "uuid",
    "hotel_name":  "Marriott Москва",
    "check_in":    "2026-07-01",
    "check_out":   "2026-07-05",
    "nights":      4,
    "total_price": 60000.0
  }
}
```

---

## booking.cancelled

| Поле | Значение |
|---|---|
| **Exchange** | `hotel_booking` (topic) |
| **Routing key** | `booking.cancelled` |
| **Producer** | API: DELETE /api/bookings/{id} |
| **Consumers** | `notifications`, `analytics`, `audit_log` |
| **Гарантии** | at-least-once |

**Payload:**
```json
{
  "event":      "booking.cancelled",
  "occurred_at":"2026-04-26T12:00:00Z",
  "payload": {
    "booking_id": "uuid",
    "user_id":    "uuid",
    "hotel_id":   "uuid",
    "hotel_name": "Marriott Москва"
  }
}
```
