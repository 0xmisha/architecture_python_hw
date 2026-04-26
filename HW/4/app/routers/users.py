from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.auth import get_current_user
from app.database import get_db
from app.schemas import UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/search", response_model=list[UserOut])
def search_users(
    login: str | None = Query(None, description="Exact login"),
    name:  str | None = Query(None, description="Name/surname mask (case-insensitive)"),
    _current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    if not login and not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide 'login' or 'name' param")

    if login:
        docs = list(db.users.find({"login": login}))
    else:
        docs = list(db.users.find({
            "$or": [
                {"first_name": {"$regex": name, "$options": "i"}},
                {"last_name":  {"$regex": name, "$options": "i"}},
            ]
        }))

    return [_out(d) for d in docs]


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: str,
    _current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    doc = db.users.find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _out(doc)


def _out(doc: dict) -> UserOut:
    return UserOut(
        id=str(doc["_id"]),
        login=doc["login"],
        first_name=doc["first_name"],
        last_name=doc["last_name"],
        email=doc["email"],
    )
