from typing import Sequence
from sqlmodel import Session, select, and_
from app.db.session import engine
from app.schemas.user import User


class UserRepository:

    def get_all(self) -> Sequence[User]:
        with Session(engine) as session:
            return session.exec(select(User)).all()

    def get_by_id(self, user_id: int) -> User:
        with Session(engine) as session:
            return session.exec(select(User).filter(User.id == user_id)).first()

    def get_by_email(self, email: str) -> User:
        with Session(engine) as session:
            return session.exec(select(User).filter(User.email == email)).first()

    def is_email_unique(self, email: str, current_id: int | None = None) -> bool:
        with Session(engine) as session:
            query = select(User)
            conditions = [User.email == email]
            if current_id:
                conditions.append(User.id != current_id)

            if len(conditions) > 1:
                query = query.where(*conditions)
            else:
                query = query.where(and_(*conditions))

            return session.exec(query).first() is None
