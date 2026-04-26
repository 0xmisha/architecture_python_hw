from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.schemas import Token, UserLogin, UserOut, UserRegister

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Database = Depends(get_db)):
    try:
        result = db.users.insert_one({
            "login":         data.login,
            "password_hash": hash_password(data.password),
            "first_name":    data.first_name,
            "last_name":     data.last_name,
            "email":         data.email,
            "created_at":    datetime.now(timezone.utc),
        })
    except DuplicateKeyError as e:
        field = "login" if "login" in str(e) else "email"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{field} already taken")

    user = db.users.find_one({"_id": result.inserted_id})
    return _out(user)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Database = Depends(get_db)):
    user = db.users.find_one({"login": data.login})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return Token(access_token=create_access_token(str(user["_id"])))


def _out(doc: dict) -> UserOut:
    return UserOut(
        id=str(doc["_id"]),
        login=doc["login"],
        first_name=doc["first_name"],
        last_name=doc["last_name"],
        email=doc["email"],
    )
