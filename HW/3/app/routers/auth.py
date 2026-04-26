from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import Token, UserLogin, UserOut, UserRegister

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.login == data.login).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login already taken")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already taken")

    user = User(
        login=data.login,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _out(user)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == data.login).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return Token(access_token=create_access_token(str(user.id)))


def _out(user: User) -> UserOut:
    return UserOut(
        id=str(user.id),
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
    )
