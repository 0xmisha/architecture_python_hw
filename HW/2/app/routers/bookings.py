from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.database import bookings, generate_id, hotels
from app.schemas import BookingCreate, BookingOut

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(data: BookingCreate, current_user: dict = Depends(get_current_user)):
    if data.hotel_id not in hotels:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")

    if data.check_out <= data.check_in:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="check_out must be after check_in")

    hotel = hotels[data.hotel_id]
    nights = (data.check_out - data.check_in).days
    total_price = nights * hotel["price_per_night"]

    booking_id = generate_id()
    bookings[booking_id] = {
        "id": booking_id,
        "user_id": current_user["id"],
        "hotel_id": data.hotel_id,
        "hotel_name": hotel["name"],
        "check_in": data.check_in,
        "check_out": data.check_out,
        "total_price": total_price,
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc),
    }
    return BookingOut(**bookings[booking_id])


@router.get("/my", response_model=list[BookingOut])
def get_my_bookings(current_user: dict = Depends(get_current_user)):
    return [
        BookingOut(**b)
        for b in bookings.values()
        if b["user_id"] == current_user["id"]
    ]


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    if booking_id not in bookings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    b = bookings[booking_id]
    if b["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return BookingOut(**b)


@router.delete("/{booking_id}", status_code=status.HTTP_200_OK)
def cancel_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    if booking_id not in bookings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    b = bookings[booking_id]
    if b["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if b["status"] == "cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking already cancelled")
    b["status"] = "cancelled"
    return {"detail": "Booking cancelled", "booking_id": booking_id}
