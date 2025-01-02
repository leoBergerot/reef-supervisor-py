from sqlmodel import Field, SQLModel
from app.schemas.timestampable import Timestampable


class Tank(SQLModel, Timestampable, table=True):
    id: int | None = Field(primary_key=True)
    name: str = Field(index=True)
    user_id: int = Field(index=True, foreign_key="user.id")
