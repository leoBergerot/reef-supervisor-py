from sqlmodel import Field, SQLModel
from app.schemas.timestampable import Timestampable


class Parameter(SQLModel, Timestampable, table=True):
    id: int | None = Field(primary_key=True)
    name: str = Field(index=True)
    sub_name: str = Field()
    need_value: bool = Field(default=True)
