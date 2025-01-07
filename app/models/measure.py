from decimal import Decimal
from typing import Annotated, Any
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from pydantic_core import InitErrorDetails

from app.repositories import ParameterRepository
from app.schemas.timestampable import Timestampable


class MeasureRequestValue(BaseModel):
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

            if parameter and not parameter.need_value and 'value' in data and data.get('value') is not None:
                raise ValidationError.from_exception_data(
                    title="Validation Error for MeasureRequest",
                    line_errors=[InitErrorDetails(**{
                        "loc": ("value",),
                        "input": data,
                        "type": "value_error",
                        "ctx": {'error': '"value" should be blank'}
                    })])
            if parameter and parameter.need_value and 'value' not in data:
                raise ValidationError.from_exception_data(
                    title="Validation Error for MeasureRequest",
                    line_errors=[InitErrorDetails(**{
                        "loc": ("value",),
                        "input": data,
                        "type": "value_error",
                        "ctx": {'error': '"value" should be not blank'}

                    })])
            return data


class MeasureResponse(MeasureRequest, Timestampable):
    id: int


class MeasureListPaginateResponse(BaseModel):
    data: list[MeasureResponse]
    total_page: int
    total: int
