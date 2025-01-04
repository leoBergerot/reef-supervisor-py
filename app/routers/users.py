from fastapi import APIRouter, Depends, HTTPException, Security
from app.managers import UserManager
from app.schemas.user import User
from app.models.user import UserRequest, UserResponse
from app.core.security import hash_password
from app.repositories.user_repository import UserRepository
from typing import Annotated
from app.core.security import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("", response_model=UserResponse)
def create_user(user: UserRequest, user_repository: Annotated[UserRepository, Depends(UserRepository)],
                user_manager: Annotated[UserManager, Depends(UserManager)]):
    if not user_repository.is_email_unique(str(user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password)
    new_user = user_manager.create_add_preferences_persist(new_user)

    return new_user.model_dump(include={"id", "email"})


@router.patch("", response_model=UserResponse)
def update_user(user: UserRequest, user_repository: Annotated[UserRepository, Depends(UserRepository)],
                current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
                user_manager: Annotated[UserManager, Depends(UserManager)]):
    if not user_repository.is_email_unique(str(user.email), current_user.id):
        raise HTTPException(status_code=400, detail="Email already registered")
    current_user = user_manager.update_persist(user, current_user)

    return current_user.model_dump(include={"id", "email"})
