from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import User
from app.models.user import UserRequest


class UserRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def get_by_id(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def is_email_unique(self, email: str, current_id: int | None = None) -> bool:
        query = self.db.query(User).filter(User.email == email)
        if current_id:
            query = query.filter(User.id != current_id)

        return query.first() is None

    def update(self, user: User, user_request: UserRequest) -> User:
        for field, value in user_request.dict(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user
