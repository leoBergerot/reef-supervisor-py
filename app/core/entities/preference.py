from datetime import datetime

from app.core.entities import Parameter
from app.core.models import PreferenceRequest, PreferenceResponse


class Preference:
    def __init__(self, id: None | int, enabled: bool, parameter: Parameter, created_at: datetime, updated_at: datetime):
        self.id = id
        self.enabled = enabled
        self.parameter = parameter
        self.created_at = created_at
        self.updated_at = updated_at

    def update(self, preference_request: PreferenceRequest):
        self.enabled = preference_request.enabled

    def to_response_view(self):
        return PreferenceResponse(
            self.enabled,
            self.id,
            self.parameter.to_response_view()
        )

