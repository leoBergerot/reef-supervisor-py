from app.core.entities import User, Preference
from app.core.models import PreferenceRequest


class PreferenceRepository:

    def get_by_user(self, user: User) -> list[Preference]:
        raise NotImplementedError()

    def get_by_id_and_user(self, id: int, user: User) -> Preference:
        raise NotImplementedError()

    def update_persist(self, preference_request: PreferenceRequest, preference: Preference) -> Preference:
        raise NotImplementedError()
