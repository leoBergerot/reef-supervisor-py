from decimal import Decimal
from typing import Annotated

from sqlmodel import Field, SQLModel
from app.schemas.timestampable import Timestampable


class Measure(SQLModel, Timestampable, table=True):
    id: int | None = Field(primary_key=True)
    parameter_id: int = Field(index=True, foreign_key="parameter.id")
    tank_id: int = Field(index=True, foreign_key="tank.id")
    value: Annotated[Decimal | None, Field(default=0, nullable=True, decimal_places=2)] = None
