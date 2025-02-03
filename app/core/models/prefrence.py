from app.core.models import ParameterResponse

class PreferenceRequest:
    def __init__(self, enabled: bool):
        self.enabled = enabled


class PreferenceResponse(PreferenceRequest):
    def __init__(self, enabled: bool, id: int, parameter: ParameterResponse):
        super().__init__(enabled)
        self.id = id
        self.parameter = parameter
