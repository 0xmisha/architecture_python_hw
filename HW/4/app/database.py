import os

from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.database import Database

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB",  "hotel_booking")

_client: MongoClient | None = None
_db: Database | None = None


def connect() -> None:
    global _client, _db
    _client = MongoClient(MONGO_URL)
    _db = _client[MONGO_DB]
    _ensure_indexes()


def disconnect() -> None:
    if _client:
        _client.close()


def get_db() -> Database:
    return _db


def _ensure_indexes() -> None:
    db = _db
    db.users.create_index("login",  unique=True)
    db.users.create_index("email",  unique=True)
    db.users.create_index([("first_name", TEXT), ("last_name", TEXT)])

    db.hotels.create_index("city")
    db.hotels.create_index("stars")

    db.bookings.create_index("user_id")
    db.bookings.create_index("hotel_id")
    db.bookings.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
    db.bookings.create_index("check_in")
