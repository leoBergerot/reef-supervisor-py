from sqlmodel import Field, SQLModel, Relationship

from app.schemas.timestampable import Timestampable
from sqlalchemy import UniqueConstraint
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON


class User(SQLModel, Timestampable, table=True):
    __table_args__ = (UniqueConstraint("email"),)
    id: int | None = Field(primary_key=True)
    email: str = Field()
    password: str = Field()
    preferences: list["Preference"] = Relationship(back_populates="user")
    scopes: list[str] = Field(sa_column=Column(JSON), default=["USER"])
