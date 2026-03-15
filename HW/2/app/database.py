from datetime import date, datetime
from uuid import uuid4

users: dict[str, dict] = {}
hotels: dict[str, dict] = {}
bookings: dict[str, dict] = {}


def generate_id() -> str:
    return uuid4().hex[:12]


def seed_data():
    """Pre-populate with sample data."""
    users.clear()
    hotels.clear()
    bookings.clear()
