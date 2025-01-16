from typing import Self

from sqlmodel import Field, SQLModel, Relationship

from app.core.entities import User as UserCore
from app.schemas.preference import Preference
from app.schemas.timestampable import Timestampable
from sqlalchemy import UniqueConstraint
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON


class User(SQLModel, Timestampable, table=True):
    __table_args__ = (UniqueConstraint("email"),)
    id: int | None = Field(primary_key=True)
    email: str = Field()
    password: str = Field()
    preferences: list[Preference] = Relationship(back_populates="user")
    scopes: list[str] = Field(sa_column=Column(JSON), default=["USER"])

    def from_core(self, user: UserCore) -> Self:
        self.id = user.id
        self.email = user.email
        self.password = user.password
        self.preferences = [(Preference()).from_core(preference) for preference in user.preferences]
        self.updated_at = user.updated_at
        self.created_at =user.created_at

        return self

    def to_core(self) -> UserCore:
        return UserCore(id=self.id, email=self.email, password=self.password, preferences=[preference.to_core() for preference in self.preferences], created_at=self.created_at, updated_at=self.updated_at)


