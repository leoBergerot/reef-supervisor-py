from app.core.entities import Parameter
from app.core.repositories import ParameterRepository
from app.core.models import ParameterRequest


class CreateParameterUseCase:

    def __init__(self, parameter_repository: ParameterRepository):
        self.parameter_repository = parameter_repository

    def execute(self, parameter_request: ParameterRequest) -> Parameter:
        return self.parameter_repository.create_persist(parameter_request)
