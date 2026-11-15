from datetime import datetime

from app.core.models import ParameterResponse, ParameterRequest


class Parameter:
    def __init__(
        self,
        id: int,
        name: str,
        sub_name: str,
        need_value: bool,
        created_at: datetime,
        updated_at: datetime,
        for_seawater: bool = True,
        for_freshwater: bool = True,
        is_custom: bool = False,
    ):
        self.id = id
        self.name = name
        self.sub_name = sub_name
        self.need_value = need_value
        self.for_seawater = for_seawater
        self.for_freshwater = for_freshwater
        self.is_custom = is_custom
        self.created_at = created_at
        self.updated_at = updated_at

    def to_response_view(self):
        return ParameterResponse(
            self.id,
            self.name,
            self.sub_name,
            self.need_value,
            self.for_seawater,
            self.for_freshwater,
            self.is_custom,
        )

    def update(self, parameter_request: ParameterRequest):
        self.name = parameter_request.name
        self.need_value = parameter_request.need_value
        self.sub_name = parameter_request.sub_name
        self.for_seawater = getattr(parameter_request, "for_seawater", self.for_seawater)
        self.for_freshwater = getattr(parameter_request, "for_freshwater", self.for_freshwater)
        # Catalog admin updates must not flip custom rows accidentally.
        if getattr(parameter_request, "is_custom", None) is not None:
            self.is_custom = parameter_request.is_custom
