from pydantic import BaseModel, Field

from app.models.parameter import ParameterResponse


class TankParameterResponse(BaseModel):
    id: int
    enabled: bool
    is_custom: bool
    sort_order: int = 0
    parameter: ParameterResponse


class TankParameterUpdateItem(BaseModel):
    parameter_id: int
    enabled: bool
    sort_order: int | None = None


class TankParameterPatchRequest(BaseModel):
    parameters: list[TankParameterUpdateItem] = Field(min_length=1)


class CustomTankParameterRequest(BaseModel):
    name: str = Field(min_length=1)
    unit: str = Field(min_length=1)
