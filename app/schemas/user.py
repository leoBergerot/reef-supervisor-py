from sqlmodel import Field, SQLModel
from app.schemas.timestampable import Timestampable
from sqlalchemy import UniqueConstraint


class User(SQLModel, Timestampable, table=True):
    __table_args__ = (UniqueConstraint("email"),)
    id: int | None = Field(primary_key=True)
    email: str = Field()
    password: str = Field()
