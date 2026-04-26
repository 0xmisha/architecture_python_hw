"""
Consumer — обрабатывает события из RabbitMQ.
Запуск: python consumer.py [notifications|analytics|audit_log]
"""

import json
import os
import sys

import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE     = "hotel_booking"

# Queue definitions: name → list of binding keys
QUEUES = {
    "notifications": ["booking.confirmed", "booking.cancelled"],
    "analytics":     ["user.*", "hotel.*", "booking.*"],
    "audit_log":     ["#"],
}

# Minimal handlers per routing key
HANDLERS = {
    "user.registered": lambda p: print(f"  [analytics] New user: {p['login']} ({p['email']})"),
    "hotel.created":   lambda p: print(f"  [analytics] New hotel: {p['name']} in {p['city']}"),
    "booking.confirmed": lambda p: print(
        f"  [notify] Booking {p['booking_id'][:8]}… confirmed — "
        f"{p['hotel_name']}, {p['check_in']}→{p['check_out']}, "
        f"{p['total_price']} ₽ → send email to user {p['user_id'][:8]}…"
    ),
    "booking.cancelled": lambda p: print(
        f"  [notify] Booking {p['booking_id'][:8]}… CANCELLED "
        f"— {p['hotel_name']} → send cancellation email"
    ),
}


def on_message(channel, method, _properties, body) -> None:
    try:
        msg     = json.loads(body)
        event   = msg.get("event", method.routing_key)
        payload = msg.get("payload", {})
        print(f"[←] {event} at {msg.get('occurred_at', '?')}")
        handler = HANDLERS.get(event)
        if handler:
            handler(payload)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as exc:
        print(f"[!] Error processing message: {exc}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main(queue_name: str) -> None:
    if queue_name not in QUEUES:
        print(f"Unknown queue. Choose from: {list(QUEUES)}")
        sys.exit(1)

    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel    = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=queue_name, durable=True)

    for key in QUEUES[queue_name]:
        channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=key)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_message)

    print(f"[*] Listening on queue '{queue_name}' (bindings: {QUEUES[queue_name]})")
    print("[*] Ctrl+C to stop\n")
    channel.start_consuming()


if __name__ == "__main__":
    queue = sys.argv[1] if len(sys.argv) > 1 else "notifications"
    main(queue)
