from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.database import users
from app.schemas import UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/search", response_model=list[UserOut])
def search_users(
    login: str | None = Query(None, description="Exact login"),
    name: str | None = Query(None, description="Name/surname mask (case-insensitive substring)"),
    _current_user: dict = Depends(get_current_user),
):
    if not login and not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide 'login' or 'name' query param")

    results = []
    for u in users.values():
        if login and u["login"] == login:
            results.append(_out(u))
        elif name:
            full = f"{u['first_name']} {u['last_name']}".lower()
            if name.lower() in full:
                results.append(_out(u))
    return results


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, _current_user: dict = Depends(get_current_user)):
    if user_id not in users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _out(users[user_id])


def _out(u: dict) -> UserOut:
    return UserOut(id=u["id"], login=u["login"], first_name=u["first_name"], last_name=u["last_name"], email=u["email"])
