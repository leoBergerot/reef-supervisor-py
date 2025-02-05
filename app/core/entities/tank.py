from datetime import datetime

from app.core.models import TankResponse


class Tank:
    def __init__(self, id: int, name: str, created_at: datetime, updated_at: datetime):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at

    def to_response_view(self):
        return TankResponse(id=self.id, name=self.name)
