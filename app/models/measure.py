from decimal import Decimal
from typing import Annotated, Any
from pydantic import BaseModel, Field, field_validator, model_validator

from app.models import ParameterResponse, TankResponse
from app.repositories import ParameterRepository
from app.schemas.timestampable import Timestampable


class Base(BaseModel):
    value: Annotated[Decimal, Field(decimal_places=2)]


class MeasureRequest(BaseModel):
    parameter_id: int
    value: Annotated[Decimal | None, Field()] = None
    tank_id: int

    @field_validator("parameter_id")
    @classmethod
    def check_parameter(cls, value: int) -> int:
        parameter = ParameterRepository().get_by_id(value)
        if parameter is None:
            raise ValueError('"Parameter" not found')
        return value

    @model_validator(mode='before')
    @classmethod
    def check_value(cls, data: Any) -> Any:
        if isinstance(data, dict) and 'parameter_id' in data:
            parameter_id = data['parameter_id']
            parameter = ParameterRepository().get_by_id(parameter_id)
            if parameter and not parameter.need_value and 'value' in data:
                raise ValueError('"value" should be blank')
            if parameter and parameter.need_value and 'value' not in data:
                raise ValueError('"value" should be not blank')
        return data

class MeasureResponse(MeasureRequest, Timestampable):
    id: int
