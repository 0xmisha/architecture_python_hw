from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Booking, Hotel, User
from app.rate_limit import make_rate_limiter
from app.schemas import BookingCreate, BookingOut

router = APIRouter(prefix="/api/bookings", tags=["bookings"])

# 10 booking attempts per minute per IP — prevents booking spam
_booking_limiter = make_rate_limiter("booking_create", limit=10, window_seconds=60)


@router.post(
    "",
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_booking_limiter)],
)
def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a hotel booking for the authenticated user.
    Rate limited: 10 requests/min per IP (Sliding Window).
    """
    hotel = db.query(Hotel).filter(Hotel.id == data.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")

    if data.check_out <= data.check_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="check_out must be after check_in",
        )

    nights      = (data.check_out - data.check_in).days
    total_price = nights * float(hotel.price_per_night)

    booking = Booking(
        user_id=current_user.id,
        hotel_id=hotel.id,
        check_in=data.check_in,
        check_out=data.check_out,
        total_price=total_price,
        status="confirmed",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return _out(booking, hotel.name)


@router.get("/my", response_model=list[BookingOut])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Booking, Hotel.name)
        .join(Hotel, Booking.hotel_id == Hotel.id)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return [_out(b, name) for b, name in rows]


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = (
        db.query(Booking, Hotel.name)
        .join(Hotel, Booking.hotel_id == Hotel.id)
        .filter(Booking.id == booking_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    booking, hotel_name = row
    if str(booking.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return _out(booking, hotel_name)


@router.delete("/{booking_id}", status_code=status.HTTP_200_OK)
def cancel_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if str(booking.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if booking.status == "cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking already cancelled")

    booking.status = "cancelled"
    db.commit()
    return {"detail": "Booking cancelled", "booking_id": booking_id}


def _out(booking: Booking, hotel_name: str) -> BookingOut:
    return BookingOut(
        id=str(booking.id),
        user_id=str(booking.user_id),
        hotel_id=str(booking.hotel_id),
        hotel_name=hotel_name,
        check_in=booking.check_in,
        check_out=booking.check_out,
        total_price=float(booking.total_price),
        status=booking.status,
        created_at=booking.created_at,
    )
