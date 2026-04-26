"""
Producer — публикует события бронирования в RabbitMQ.
Запуск: python producer.py
"""

import json
import os
import uuid
from datetime import datetime, timezone

import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE     = "hotel_booking"


def publish(channel: pika.channel.Channel, routing_key: str, payload: dict) -> None:
    message = {
        "event":       routing_key,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "payload":     payload,
    }
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,        # persistent
            content_type="application/json",
        ),
    )
    print(f"[→] {routing_key}: {json.dumps(payload)}")


def main() -> None:
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel    = connection.channel()

    # Declare durable topic exchange
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    # ---- simulate a session ----

    user_id    = str(uuid.uuid4())
    hotel_id   = str(uuid.uuid4())
    booking_id = str(uuid.uuid4())

    publish(channel, "user.registered", {
        "user_id": user_id,
        "login":   "ivan_petrov",
        "email":   "ivan@mail.ru",
    })

    publish(channel, "hotel.created", {
        "hotel_id":        hotel_id,
        "name":            "Marriott Москва",
        "city":            "Москва",
        "stars":           5,
        "price_per_night": 15000.0,
    })

    publish(channel, "booking.confirmed", {
        "booking_id":  booking_id,
        "user_id":     user_id,
        "hotel_id":    hotel_id,
        "hotel_name":  "Marriott Москва",
        "check_in":    "2026-07-01",
        "check_out":   "2026-07-05",
        "nights":      4,
        "total_price": 60000.0,
    })

    publish(channel, "booking.cancelled", {
        "booking_id": booking_id,
        "user_id":    user_id,
        "hotel_id":   hotel_id,
        "hotel_name": "Marriott Москва",
    })

    connection.close()
    print("[✓] Done")


if __name__ == "__main__":
    main()
