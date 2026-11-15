from typing import Literal

from pydantic import BaseModel, Field

from app.core.models import TankRequest as TankRequestCore


WaterType = Literal["seawater", "freshwater"]


class CustomParameterInput(BaseModel):
    name: str = Field(min_length=1)
    unit: str = Field(min_length=1)


class TankRequest(BaseModel):
    name: str = Field(min_length=1)
    water_type: WaterType
    enabled_parameter_ids: list[int] | None = None
    custom_parameters: list[CustomParameterInput] | None = None

    def to_core(self):
        return TankRequestCore(
            self.name,
            self.water_type,
            self.enabled_parameter_ids,
            [item.model_dump() for item in self.custom_parameters] if self.custom_parameters else [],
        )


class TankRenameRequest(BaseModel):
    name: str = Field(min_length=1)


class TankResponse(BaseModel):
    id: int
    name: str
    water_type: WaterType
    photo_url: str | None = None
