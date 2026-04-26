from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Hotel, User
from app.schemas import HotelCreate, HotelOut

router = APIRouter(prefix="/api/hotels", tags=["hotels"])


@router.post("", response_model=HotelOut, status_code=status.HTTP_201_CREATED)
def create_hotel(
    data: HotelCreate,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    hotel = Hotel(
        name=data.name,
        city=data.city,
        address=data.address,
        stars=data.stars,
        rooms_total=data.rooms_total,
        price_per_night=data.price_per_night,
    )
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return _out(hotel)


@router.get("", response_model=list[HotelOut])
def list_hotels(db: Session = Depends(get_db)):
    return [_out(h) for h in db.query(Hotel).order_by(Hotel.city, Hotel.name).all()]


@router.get("/search", response_model=list[HotelOut])
def search_hotels_by_city(
    city: str = Query(..., description="City name (case-insensitive substring)"),
    db: Session = Depends(get_db),
):
    hotels = (
        db.query(Hotel)
        .filter(Hotel.city.ilike(f"%{city}%"))
        .order_by(Hotel.stars.desc(), Hotel.price_per_night)
        .all()
    )
    return [_out(h) for h in hotels]


@router.get("/{hotel_id}", response_model=HotelOut)
def get_hotel(hotel_id: str, db: Session = Depends(get_db)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return _out(hotel)


def _out(hotel: Hotel) -> HotelOut:
    return HotelOut(
        id=str(hotel.id),
        name=hotel.name,
        city=hotel.city,
        address=hotel.address,
        stars=hotel.stars,
        rooms_total=hotel.rooms_total,
        price_per_night=float(hotel.price_per_night),
    )
