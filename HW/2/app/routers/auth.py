from fastapi import APIRouter, HTTPException, status

from app.auth import create_access_token, hash_password, verify_password
from app.database import generate_id, users
from app.schemas import Token, UserLogin, UserOut, UserRegister

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister):
    for u in users.values():
        if u["login"] == data.login:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login already exists")

    user_id = generate_id()
    users[user_id] = {
        "id": user_id,
        "login": data.login,
        "password_hash": hash_password(data.password),
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
    }
    return _user_out(users[user_id])


@router.post("/login", response_model=Token)
def login(data: UserLogin):
    user = _find_by_login(data.login)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return Token(access_token=create_access_token(user["id"]))


def _find_by_login(login: str):
    for u in users.values():
        if u["login"] == login:
            return u
    return None


def _user_out(u: dict) -> UserOut:
    return UserOut(id=u["id"], login=u["login"], first_name=u["first_name"], last_name=u["last_name"], email=u["email"])
