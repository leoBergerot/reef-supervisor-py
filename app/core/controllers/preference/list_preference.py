from app.core.entities import User
from app.core.models import PreferenceResponse
from app.core.repositories import PreferenceRepository


class ListPreferenceUseCase:
    def __init__(self, preference_repository: PreferenceRepository):
        self.preference_repository = preference_repository

    def execute(self, user: User) -> list[PreferenceResponse]:
        return [preference.to_response_view() for preference in self.preference_repository.get_by_user(user)]
