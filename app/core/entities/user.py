from app.core.entities import Preference
from datetime import datetime


class User:
    def __init__(self, id: int, email: str, password: str, preferences: list[Preference], created_at: datetime, updated_at: datetime):
        self.id = id
        self.email = email
        self.password = password
        self.preferences = preferences
        self.created_at = created_at
        self.updated_at = updated_at
