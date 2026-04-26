from datetime import date, datetime
from pydantic import BaseModel, Field


# модели для авторизации

class UserRegister(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)  # минимум 4 символа — не очень строго, но для учебного проекта норм
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: str  # валидацию email не делал, pydantic v2 это через EmailStr, не хотелось тащить доп зависимость


class UserLogin(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# то что отдаём наружу — пароль сюда не включаем очевидно

class UserOut(BaseModel):
    id: str
    login: str
    first_name: str
    last_name: str
    email: str


# отели

class HotelCreate(BaseModel):
    name: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    stars: int = Field(..., ge=1, le=5)
    rooms_total: int = Field(..., ge=1)
    price_per_night: float = Field(..., gt=0)


class HotelOut(BaseModel):
    id: str
    name: str
    city: str
    address: str
    stars: int
    rooms_total: int
    price_per_night: float


# бронирования

class BookingCreate(BaseModel):
    hotel_id: str
    check_in: date
    check_out: date
    # total_price не принимаем от клиента — считаем сами на сервере


class BookingOut(BaseModel):
    id: str
    user_id: str
    hotel_id: str
    hotel_name: str  # денормализовано для удобства — чтоб не делать отдельный запрос за названием
    check_in: date
    check_out: date
    total_price: float
    status: str
    created_at: datetime
