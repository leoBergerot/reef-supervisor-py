from fastapi import APIRouter, Depends, HTTPException
from typing import Union
from app.schemas.user import User
from app.models.user import UserRequest, UserResponse
from app.core.security import hash_password
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("", response_model=UserResponse)
def create_user(user: UserRequest, db: Session = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(db)
    if not user_repository.is_email_unique(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password)
    user_repository.create(new_user)
    return new_user.dict(include={"id", "email"})
