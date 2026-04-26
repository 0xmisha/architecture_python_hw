from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import database
from app.routers import auth, bookings, hotels, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.connect()
    yield
    database.disconnect()


app = FastAPI(
    title="Hotel Booking API",
    description="REST API для системы бронирования отелей (Вариант 13) — MongoDB edition",
    version="3.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(hotels.router)
app.include_router(bookings.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "Hotel Booking API (MongoDB)"}
