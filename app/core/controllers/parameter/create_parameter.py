from datetime import datetime, UTC

from app.core.entities import Parameter, Preference
from app.core.repositories import ParameterRepository, UserRepository
from app.core.models import ParameterRequest


class CreateParameterUseCase:

    def __init__(self, parameter_repository: ParameterRepository, user_repository: UserRepository):
        self.parameter_repository = parameter_repository
        self.user_repository = user_repository

    def execute(self, parameter_request: ParameterRequest) -> Parameter:
        parameter = self.parameter_repository.create_persist(parameter_request)
        users = self.user_repository.get_all()

        for user in users:
            user.preferences.append(Preference(id=None, parameter=parameter, enabled=True, created_at= datetime.now(UTC), updated_at=datetime.now(UTC) ))

        self.user_repository.save_alls(users)
        return parameter
