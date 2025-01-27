from datetime import datetime

from app.core.entities import Parameter


class Preference:
    def __init__(self, id: None|int, enabled: bool, parameter: Parameter, created_at: datetime, updated_at: datetime):
        self.id = id
        self.enabled = enabled
        self.parameter = parameter
        self.created_at = created_at
        self.updated_at = updated_at
