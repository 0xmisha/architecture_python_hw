import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login         = Column(String(50),  nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name    = Column(String(100), nullable=False)
    last_name     = Column(String(100), nullable=False)
    email         = Column(String(255), nullable=False, unique=True)
    created_at    = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")


class Hotel(Base):
    __tablename__ = "hotels"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name            = Column(String(255),   nullable=False)
    city            = Column(String(100),   nullable=False)
    address         = Column(String(500),   nullable=False)
    stars           = Column(SmallInteger,  nullable=False)
    rooms_total     = Column(Integer,       nullable=False)
    price_per_night = Column(Numeric(12, 2),nullable=False)
    created_at      = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    bookings = relationship("Booking", back_populates="hotel", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("stars BETWEEN 1 AND 5",  name="chk_hotels_stars"),
        CheckConstraint("rooms_total > 0",         name="chk_hotels_rooms_total"),
        CheckConstraint("price_per_night > 0",     name="chk_hotels_price"),
    )


class Booking(Base):
    __tablename__ = "bookings"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id",  ondelete="CASCADE"), nullable=False)
    hotel_id    = Column(UUID(as_uuid=True), ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    check_in    = Column(Date,           nullable=False)
    check_out   = Column(Date,           nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    status      = Column(String(20),     nullable=False, default="confirmed")
    created_at  = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user  = relationship("User",  back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")

    __table_args__ = (
        CheckConstraint("check_out > check_in",                       name="chk_booking_dates"),
        CheckConstraint("total_price >= 0",                            name="chk_booking_price"),
        CheckConstraint("status IN ('confirmed', 'cancelled')",        name="chk_booking_status"),
    )
