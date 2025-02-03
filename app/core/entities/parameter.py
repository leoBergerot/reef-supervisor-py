from datetime import datetime

from app.core.models import ParameterResponse, ParameterRequest


class Parameter:
    def __init__(self, id: int, name: str, sub_name: str, need_value: bool, created_at: datetime, updated_at: datetime):
        self.id = id
        self.name = name
        self.sub_name = sub_name
        self.need_value = need_value
        self.created_at = created_at
        self.updated_at = updated_at

    def to_response_view(self):
        return ParameterResponse(
            self.id,
            self.name,
            self.sub_name,
            self.need_value
        )

    def update(self, parameter_request: ParameterRequest):
        self.name = parameter_request.name
        self.need_value = parameter_request.need_value
        self.sub_name = parameter_request.sub_name
