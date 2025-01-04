from pydantic import BaseModel


class ParameterRequest(BaseModel):
    name: str
    sub_name: str
    need_value: bool


class ParameterResponse(ParameterRequest):
    id: int