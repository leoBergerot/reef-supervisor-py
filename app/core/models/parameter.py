class ParameterRequest:
    def __init__(
        self,
        name: str,
        sub_name: str,
        need_value: bool,
        for_seawater: bool = True,
        for_freshwater: bool = True,
        is_custom: bool = False,
    ):
        self.name = name
        self.sub_name = sub_name
        self.need_value = need_value
        self.for_seawater = for_seawater
        self.for_freshwater = for_freshwater
        self.is_custom = is_custom


class ParameterResponse(ParameterRequest):
    def __init__(
        self,
        id: int,
        name: str,
        sub_name: str,
        need_value: bool,
        for_seawater: bool = True,
        for_freshwater: bool = True,
        is_custom: bool = False,
    ):
        super().__init__(name, sub_name, need_value, for_seawater, for_freshwater, is_custom)
        self.id = id
