from app.core.models import ParameterResponse
from app.core.repositories import ParameterRepository


class ListParameterUseCase:
    def __init__(self, parameter_repository: ParameterRepository):
        self.parameter_repository = parameter_repository

    def execute(self, name: str, ids: list[int]) -> list[ParameterResponse]:
        return [parameter.to_request_view() for parameter in self.parameter_repository.get_by_filter(name, ids)]