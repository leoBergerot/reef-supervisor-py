from app.core.models import ParameterRequest, ParameterResponse
from app.core.repositories import ParameterRepository


class UpdateParameterUseCase:
    def __init__(self, parameter_repository: ParameterRepository):
        self.parameter_repository = parameter_repository

    def execute(self, parameter_id: int, parameter_request: ParameterRequest) -> ParameterResponse:
        parameter = self.parameter_repository.get_by_id(parameter_id)
        if parameter is None:
            raise Exception({'status_code': 404, 'detail': "Parameter not found"})

        return self.parameter_repository.update_persist(parameter, parameter_request).to_response_view()
