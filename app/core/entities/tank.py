from datetime import datetime

from app.core.models import TankResponse


class Tank:
    def __init__(self, id: int, name: str, created_at: datetime, updated_at: datetime, photo_path: str | None = None):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at
        self.photo_path = photo_path

    def to_response_view(self):
        photo_url = f"/tanks/{self.id}/photo" if self.photo_path else None
        return TankResponse(id=self.id, name=self.name, photo_url=photo_url)
