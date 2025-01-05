from typing import Sequence
from sqlmodel import Session, select, and_, col
from app.db.session import engine
from app.schemas.user import User


class UserRepository:

    def get_all(self) -> Sequence[User]:
        with Session(engine) as session:
            return session.exec(select(User)).all()

    def get_by_id(self, user_id: int) -> User:
        with Session(engine) as session:
            return session.exec(select(User).filter(col(User.id == user_id))).first()

    def get_by_email(self, email: str) -> User:
        with Session(engine) as session:
            return session.exec(select(User).filter(col(User.email == email))).first()

    def is_email_unique(self, email: str, current_id: int | None = None) -> bool:
        with Session(engine) as session:
            conditions = [User.email == email]
            if current_id:
                conditions.append(User.id != current_id)
            return session.exec(
                select(User).filter(and_(*conditions))).first() is None
