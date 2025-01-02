from sqlmodel import Field, SQLModel
from app.schemas.timestampable import Timestampable


class Preference(SQLModel, Timestampable, table=True):
    id: int | None = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    parameter_id: int = Field(foreign_key="parameter.id")
    enabled: bool = Field()
