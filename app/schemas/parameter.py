from typing import Self

from sqlmodel import Field, SQLModel

from app.core.models import ParameterRequest as ParameterRequestCore
from app.schemas.timestampable import Timestampable
from app.core.entities import Parameter as ParameterCore


class Parameter(SQLModel, Timestampable, table=True):
    id: int | None = Field(primary_key=True)
    name: str = Field(index=True)
    sub_name: str = Field()
    need_value: bool = Field(default=True)
    for_seawater: bool = Field(default=True)
    for_freshwater: bool = Field(default=True)
    is_custom: bool = Field(default=False)

    def from_core_request(self, parameter_request: ParameterRequestCore) -> Self:
        self.name = parameter_request.name
        self.sub_name = parameter_request.sub_name
        self.need_value = parameter_request.need_value
        self.for_seawater = getattr(parameter_request, "for_seawater", True)
        self.for_freshwater = getattr(parameter_request, "for_freshwater", True)
        self.is_custom = getattr(parameter_request, "is_custom", False)

        return self

    def from_core(self, parameter: ParameterCore) -> Self:
        self.id = parameter.id
        self.name = parameter.name
        self.sub_name = parameter.sub_name
        self.need_value = parameter.need_value
        self.for_seawater = parameter.for_seawater
        self.for_freshwater = parameter.for_freshwater
        self.is_custom = parameter.is_custom
        self.created_at = parameter.created_at
        self.updated_at = parameter.updated_at

        return self

    def to_core(self) -> ParameterCore:
        return ParameterCore(
            id=self.id,
            name=self.name,
            sub_name=self.sub_name,
            need_value=self.need_value,
            for_seawater=self.for_seawater,
            for_freshwater=self.for_freshwater,
            is_custom=self.is_custom,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
