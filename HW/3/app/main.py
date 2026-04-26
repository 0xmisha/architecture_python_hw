from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, bookings, hotels, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hotel Booking API",
    description="REST API для системы бронирования отелей (Вариант 13) — PostgreSQL edition",
    version="2.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(hotels.router)
app.include_router(bookings.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "Hotel Booking API"}
