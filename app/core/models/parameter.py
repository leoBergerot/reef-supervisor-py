class ParameterRequest:
    def __init__(self, name: str, sub_name: str, need_value: bool):
        self.name = name
        self.sub_name = sub_name
        self.need_value = need_value

class ParameterResponse(ParameterRequest):
    def __init__(self, id: int, name: str, sub_name: str, need_value: bool):
        super().__init__(name, sub_name, need_value)
        self.id = id
