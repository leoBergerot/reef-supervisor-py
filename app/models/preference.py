from pydantic import BaseModel

class PreferenceRequest(BaseModel):
    enabled: bool

class PreferenceResponse(PreferenceRequest):
    id: int
    parameter_id: int