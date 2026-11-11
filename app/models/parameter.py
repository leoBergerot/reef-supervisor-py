from pydantic import BaseModel, Field
from app.core.models.parameter import ParameterRequest as ParameterRequestCore


class ParameterRange(BaseModel):
    """Recommended numeric band for soft UI warnings (never blocks saves)."""

    min: float
    max: float
    soft_min: float | None = None
    soft_max: float | None = None


class ParameterRangeEntry(ParameterRange):
    name: str = Field(min_length=1)


class ParameterRequest(BaseModel):
    name: str
    sub_name: str
    need_value: bool
    for_seawater: bool = True
    for_freshwater: bool = True

    def to_core(self) -> ParameterRequestCore:
        return ParameterRequestCore(
            name=self.name,
            sub_name=self.sub_name,
            need_value=self.need_value,
            for_seawater=self.for_seawater,
            for_freshwater=self.for_freshwater,
            is_custom=False,
        )


class ParameterResponse(ParameterRequest):
    id: int
    is_custom: bool = False
    # Optional recommended band for the caller's water type (additive; null when unknown).
    range: ParameterRange | None = None
