from typing import Annotated, Type
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import User


class UserRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def get_all(self) -> list[Type[User]]:
        return self.db.query(User).all()

    def get_by_id(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def is_email_unique(self, email: str, current_id: int | None = None) -> bool:
        query = self.db.query(User).filter(User.email == email)
        if current_id:
            query = query.filter(User.id != current_id)

        return query.first() is None
