from sqlmodel import Field, SQLModel

from app.schemas.timestampable import Timestampable


class TankParameter(SQLModel, Timestampable, table=True):
    __tablename__ = "tank_parameter"

    id: int | None = Field(primary_key=True)
    tank_id: int = Field(index=True, foreign_key="tank.id")
    parameter_id: int = Field(index=True, foreign_key="parameter.id")
    enabled: bool = Field(default=True)
