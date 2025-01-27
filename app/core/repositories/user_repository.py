from app.core.entities import User


class UserRepository:
    def get_all(self) -> list[User]:
        raise NotImplementedError()

    def get_by_id(self, user_id: int) -> User:
        raise NotImplementedError()
    
    def get_by_email(self, email: str) -> User:
        raise NotImplementedError()

    def is_email_unique(self, email: str, current_id: int | None = None) -> bool:
        raise NotImplementedError()

    def save_alls(self, users: list[User]):
        raise NotImplementedError()
