from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from app.auth import get_current_user
from app.database import get_db
from app.schemas import BookingCreate, BookingOut

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    hotel = db.hotels.find_one({"_id": ObjectId(data.hotel_id)})
    if not hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")

    if data.check_out <= data.check_in:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="check_out must be after check_in")

    nights      = (data.check_out - data.check_in).days
    total_price = nights * float(hotel["price_per_night"])

    doc = {
        "user_id":  current_user["_id"],
        "hotel_id": hotel["_id"],
        "hotel_snapshot": {
            "name":            hotel["name"],
            "city":            hotel["city"],
            "price_per_night": float(hotel["price_per_night"]),
        },
        "check_in":    datetime.combine(data.check_in,  datetime.min.time()),
        "check_out":   datetime.combine(data.check_out, datetime.min.time()),
        "nights":      nights,
        "total_price": total_price,
        "status":      "confirmed",
        "created_at":  datetime.now(timezone.utc),
    }
    result = db.bookings.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _out(doc)


@router.get("/my", response_model=list[BookingOut])
def get_my_bookings(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    docs = list(
        db.bookings
        .find({"user_id": current_user["_id"]})
        .sort("created_at", -1)
    )
    return [_out(d) for d in docs]


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    doc = db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if doc["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return _out(doc)


@router.delete("/{booking_id}", status_code=status.HTTP_200_OK)
def cancel_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    doc = db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if doc["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if doc["status"] == "cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking already cancelled")

    db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": "cancelled"}},
    )
    return {"detail": "Booking cancelled", "booking_id": booking_id}


def _out(doc: dict) -> BookingOut:
    snap = doc.get("hotel_snapshot", {})
    return BookingOut(
        id=str(doc["_id"]),
        user_id=str(doc["user_id"]),
        hotel_id=str(doc["hotel_id"]),
        hotel_name=snap.get("name", ""),
        hotel_city=snap.get("city", ""),
        check_in=doc["check_in"].date() if hasattr(doc["check_in"], "date") else doc["check_in"],
        check_out=doc["check_out"].date() if hasattr(doc["check_out"], "date") else doc["check_out"],
        nights=doc.get("nights", 0),
        total_price=float(doc["total_price"]),
        status=doc["status"],
        created_at=doc["created_at"],
    )
