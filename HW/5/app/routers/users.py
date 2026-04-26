from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/search", response_model=list[UserOut])
def search_users(
    login: str | None = Query(None, description="Exact login"),
    name:  str | None = Query(None, description="Name/surname mask (case-insensitive)"),
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not login and not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide 'login' or 'name' query param",
        )

    if login:
        users = db.query(User).filter(User.login == login).all()
    else:
        users = db.query(User).filter(
            or_(
                User.first_name.ilike(f"%{name}%"),
                User.last_name.ilike(f"%{name}%"),
            )
        ).all()

    return [_out(u) for u in users]


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: str,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _out(user)


def _out(user: User) -> UserOut:
    return UserOut(
        id=str(user.id),
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
    )
