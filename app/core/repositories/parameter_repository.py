from app.core.entities import Parameter
from app.core.models import ParameterRequest


class ParameterRepository:
    def get_all(self) -> list[Parameter]:
        raise NotImplementedError

    def get_by_id(self, parameter_id: int) -> Parameter:
        raise NotImplementedError

    def get_by_filter(self, name: str | None, ids: list[int] | None) -> list[Parameter]:
        raise NotImplementedError

    def create_persist(self, parameter_request: ParameterRequest) -> Parameter:
        raise NotImplementedError

    def update_persist(self, parameter: Parameter, parameter_request: ParameterRequest) -> Parameter:
        raise NotImplementedError

    def _update_user_preferences(self, parameter: Parameter):
        raise NotImplementedError