from sqlmodel import Session, select, and_, col
from app.core.repositories import UserRepository as UserRepositoryCore
from app.db.session import engine
from app.schemas.user import User
from app.core.entities import User as UserCore


class UserRepository(UserRepositoryCore):

    def get_all(self) -> list[UserCore]:
        with Session(engine) as session:
            return [user.to_core() for user in list(session.exec(select(User)).all())]

    def get_by_id(self, user_id: int) -> UserCore:
        with Session(engine) as session:
            return session.exec(select(User).filter(col(User.id) == user_id)).first()

    def is_email_unique(self, email: str, current_id: int | None = None) -> bool:
        with Session(engine) as session:
            conditions = [User.email == email]
            if current_id:
                conditions.append(User.id != current_id)
            return session.exec(
                select(User).filter(and_(*conditions))).first() is None

    def save_alls(self, users: list[User]):
        with Session(engine) as session:
            for user in users:
                user_app = (User().from_core(user))
                session.merge(user_app)
                session.commit()

    def get_by_email(self, email: str) -> UserCore:
        with Session(engine) as session:
            return session.exec(select(User).filter(col(User.email) == email)).first()

    def update_password(self, user_id: int, hashed_password: str) -> User | None:
        with Session(engine) as session:
            user = session.get(User, user_id)
            if user is None:
                return None
            user.password = hashed_password
            session.add(user)
            session.commit()
            session.refresh(user)
            session.expunge(user)
            return user

    def mark_active(self, user_id: int) -> User | None:
        with Session(engine) as session:
            user = session.get(User, user_id)
            if user is None:
                return None
            user.is_active = True
            session.add(user)
            session.commit()
            session.refresh(user)
            session.expunge(user)
            return user
