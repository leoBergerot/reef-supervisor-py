from pydantic import BaseModel
from app.core.models.parameter import ParameterRequest as ParameterRequestApplication

class ParameterRequest(BaseModel):
    name: str
    sub_name: str
    need_value: bool

    def to_application(self) -> ParameterRequestApplication:
        return ParameterRequestApplication(name=self.name, sub_name=self.sub_name, need_value=self.need_value)


class ParameterResponse(ParameterRequest):
    id: int