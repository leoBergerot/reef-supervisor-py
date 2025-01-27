from typing import Self

from sqlmodel import Field, SQLModel, Relationship

from app.schemas.timestampable import Timestampable
from app.core.entities import Preference as PreferenceCore


class Preference(SQLModel, Timestampable, table=True):
    id: int | None = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="preferences")
    parameter_id: int = Field(foreign_key="parameter.id")
    parameter: "Parameter" = Relationship()
    enabled: bool = Field()

    def from_core(self, preference: PreferenceCore)-> Self:
        self.id = preference.id
        self.parameter_id = preference.parameter.id
        self.enabled = preference.enabled
        self.created_at = preference.created_at
        self.updated_at = preference.updated_at
        return self

    def to_core(self) -> PreferenceCore:
        return PreferenceCore(id=self.id, enabled=self.enabled, parameter=self.parameter.to_core(),
                              created_at=self.created_at, updated_at=self.updated_at)
