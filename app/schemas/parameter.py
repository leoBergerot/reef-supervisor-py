from typing import Self

from sqlmodel import Field, SQLModel

from app.core.models import ParameterRequest
from app.schemas.timestampable import Timestampable


class Parameter(SQLModel, Timestampable, table=True):
    id: int | None = Field(primary_key=True)
    name: str = Field(index=True)
    sub_name: str = Field()
    need_value: bool = Field(default=True)

    def from_application(self, parameter_request: ParameterRequest) -> Self:
        self.name = parameter_request.name
        self.sub_name = parameter_request.sub_name
        self.need_value = parameter_request.need_value

        return self
