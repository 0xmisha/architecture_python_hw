from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.auth import get_current_user
from app.database import get_db
from app.schemas import HotelCreate, HotelOut

router = APIRouter(prefix="/api/hotels", tags=["hotels"])


@router.post("", response_model=HotelOut, status_code=status.HTTP_201_CREATED)
def create_hotel(
    data: HotelCreate,
    _current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    doc = {
        "name":            data.name,
        "city":            data.city,
        "address":         data.address,
        "stars":           data.stars,
        "rooms_total":     data.rooms_total,
        "price_per_night": data.price_per_night,
        "amenities":       data.amenities,
        "created_at":      datetime.now(timezone.utc),
    }
    result = db.hotels.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _out(doc)


@router.get("", response_model=list[HotelOut])
def list_hotels(db: Database = Depends(get_db)):
    docs = list(db.hotels.find({}).sort([("city", 1), ("name", 1)]))
    return [_out(d) for d in docs]


@router.get("/search", response_model=list[HotelOut])
def search_hotels_by_city(
    city: str = Query(..., description="City name (case-insensitive substring)"),
    db: Database = Depends(get_db),
):
    docs = list(
        db.hotels
        .find({"city": {"$regex": city, "$options": "i"}})
        .sort([("stars", -1), ("price_per_night", 1)])
    )
    return [_out(d) for d in docs]


@router.get("/{hotel_id}", response_model=HotelOut)
def get_hotel(hotel_id: str, db: Database = Depends(get_db)):
    doc = db.hotels.find_one({"_id": ObjectId(hotel_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return _out(doc)


def _out(doc: dict) -> HotelOut:
    return HotelOut(
        id=str(doc["_id"]),
        name=doc["name"],
        city=doc["city"],
        address=doc["address"],
        stars=doc["stars"],
        rooms_total=doc["rooms_total"],
        price_per_night=float(doc["price_per_night"]),
        amenities=doc.get("amenities", []),
    )
