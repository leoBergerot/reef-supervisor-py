class Parameter:
    def __init__(self, id: int, name: str, sub_name: str, need_value: bool):
        self.id = id
        self.name = name
        self.sub_name = sub_name
        self.need_value = need_value