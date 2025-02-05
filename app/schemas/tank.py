from sqlmodel import Field, SQLModel

from app.core.models import TankRequest
from app.core.entities import Tank as TankCore
from app.schemas.timestampable import Timestampable


class Tank(SQLModel, Timestampable, table=True):
    id: int | None = Field(primary_key=True)
    name: str = Field(index=True)
    user_id: int = Field(index=True, foreign_key="user.id")

    def from_request(self, tank_request: TankRequest):
        self.name = tank_request.name

        return self

    def to_core(self):
        return TankCore(id=self.id, name=self.name, created_at=self.created_at,
                        updated_at=self.updated_at)
