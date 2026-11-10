from pydantic import BaseModel
from app.core.models.parameter import ParameterRequest as ParameterRequestCore


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
