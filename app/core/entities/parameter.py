from datetime import datetime


class Parameter:
    def __init__(self, id: int, name: str, sub_name: str, need_value: bool, created_at: datetime, updated_at: datetime):
        self.id = id
        self.name = name
        self.sub_name = sub_name
        self.need_value = need_value
        self.created_at = created_at
        self.updated_at = updated_at