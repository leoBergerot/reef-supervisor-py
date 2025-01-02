from sqlalchemy.orm import Session
from app.schemas.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def is_email_unique(self, email: str) -> bool:
        return self.db.query(User).filter(User.email == email).first() is None

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
