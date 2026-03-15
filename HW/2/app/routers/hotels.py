from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.database import generate_id, hotels
from app.schemas import HotelCreate, HotelOut

router = APIRouter(prefix="/api/hotels", tags=["hotels"])


@router.post("", response_model=HotelOut, status_code=status.HTTP_201_CREATED)
def create_hotel(data: HotelCreate, _current_user: dict = Depends(get_current_user)):
    hotel_id = generate_id()
    hotels[hotel_id] = {
        "id": hotel_id,
        "name": data.name,
        "city": data.city,
        "address": data.address,
        "stars": data.stars,
        "rooms_total": data.rooms_total,
        "price_per_night": data.price_per_night,
    }
    return HotelOut(**hotels[hotel_id])


@router.get("", response_model=list[HotelOut])
def list_hotels():
    return [HotelOut(**h) for h in hotels.values()]


@router.get("/search", response_model=list[HotelOut])
def search_hotels_by_city(city: str = Query(..., description="City name (case-insensitive substring)")):
    results = [
        HotelOut(**h)
        for h in hotels.values()
        if city.lower() in h["city"].lower()
    ]
    return results


@router.get("/{hotel_id}", response_model=HotelOut)
def get_hotel(hotel_id: str):
    if hotel_id not in hotels:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return HotelOut(**hotels[hotel_id])
