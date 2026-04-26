from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.cache import cache_delete, cache_delete_pattern, cache_get, cache_set, HOTEL_TTL
from app.database import get_db
from app.models import Hotel, User
from app.rate_limit import make_rate_limiter
from app.schemas import HotelCreate, HotelOut

router = APIRouter(prefix="/api/hotels", tags=["hotels"])

_search_limiter = make_rate_limiter("hotel_search", limit=30, window_seconds=60)


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

    # Invalidate list and city caches — new hotel must appear immediately
    cache_delete("hotels:list")
    cache_delete_pattern("hotels:city:*")

    return _out(hotel)


@router.get("", response_model=list[HotelOut])
def list_hotels(response: Response, db: Session = Depends(get_db)):
    """
    Returns all hotels.
    Cache-Aside: cached in Redis for 5 minutes.
    Sets X-Cache header to HIT or MISS for observability.
    """
    cached = cache_get("hotels:list")
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return cached

    hotels = db.query(Hotel).order_by(Hotel.city, Hotel.name).all()
    result = [_out(h).model_dump() for h in hotels]
    cache_set("hotels:list", result, HOTEL_TTL)
    response.headers["X-Cache"] = "MISS"
    return result


@router.get("/search", response_model=list[HotelOut],
            dependencies=[Depends(_search_limiter)])
def search_hotels_by_city(
    city: str = Query(..., description="City name (case-insensitive substring)"),
    response: Response = None,
    db: Session = Depends(get_db),
):
    """
    Searches hotels by city substring.
    Cache-Aside: result cached per city query (case-folded key).
    Rate limited: 30 requests/min per IP (Sliding Window).
    """
    cache_key = f"hotels:city:{city.strip().lower()}"
    cached = cache_get(cache_key)
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return cached

    hotels = (
        db.query(Hotel)
        .filter(Hotel.city.ilike(f"%{city}%"))
        .order_by(Hotel.stars.desc(), Hotel.price_per_night)
        .all()
    )
    result = [_out(h).model_dump() for h in hotels]
    cache_set(cache_key, result, HOTEL_TTL)
    response.headers["X-Cache"] = "MISS"
    return result


@router.get("/{hotel_id}", response_model=HotelOut)
def get_hotel(hotel_id: str, response: Response, db: Session = Depends(get_db)):
    """
    Returns a single hotel by ID.
    Cache-Aside: cached per hotel ID for 5 minutes.
    """
    cache_key = f"hotels:one:{hotel_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return cached

    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")

    result = _out(hotel).model_dump()
    cache_set(cache_key, result, HOTEL_TTL)
    response.headers["X-Cache"] = "MISS"
    return result


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
