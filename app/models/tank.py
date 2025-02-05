from pydantic import BaseModel

from app.core.models import TankRequest as TankRequestCore


class TankRequest(BaseModel):
    name: str

    def to_core(self):
        return TankRequestCore(self.name)


class TankResponse(TankRequest):
    id: int
