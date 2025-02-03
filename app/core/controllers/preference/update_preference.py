from app.core.entities import User
from app.core.models import PreferenceRequest, PreferenceResponse
from app.core.repositories import PreferenceRepository


class UpdatePreferenceUseCase:
    def __init__(self, preference_repository: PreferenceRepository):
        self.preference_repository = preference_repository

    def execute(self, preference_id: int, preference_request: PreferenceRequest, user: User) -> PreferenceResponse:
        preference = self.preference_repository.get_by_id_and_user(preference_id, user)

        if preference is None:
            raise Exception({'status_code': 404, 'detail': "Preference not found"})

        return self.preference_repository.update_persist(preference_request, preference).to_response_view()
