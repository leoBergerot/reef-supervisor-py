from pydantic import BaseModel

from app.models import ParameterResponse


class PreferenceRequest(BaseModel):
    enabled: bool

class PreferenceResponse(PreferenceRequest):
    id: int
    parameter: ParameterResponse