from pydantic import BaseModel, Field

from app.core.models import TankRequest as TankRequestCore


class TankRequest(BaseModel):
    name: str = Field(min_length=1)

    def to_core(self):
        return TankRequestCore(self.name)


class TankResponse(TankRequest):
    id: int
    photo_url: str | None = None
