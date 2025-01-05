from sqlmodel import Field, SQLModel, Relationship

from app.schemas.timestampable import Timestampable


class Preference(SQLModel, Timestampable, table=True):
    id: int | None = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="preferences")
    parameter_id: int = Field(foreign_key="parameter.id")
    parameter: "Parameter" = Relationship()
    enabled: bool = Field()
