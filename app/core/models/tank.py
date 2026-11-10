class TankRequest:
    def __init__(
        self,
        name: str,
        water_type: str,
        enabled_parameter_ids: list[int] | None = None,
        custom_parameters: list[dict] | None = None,
    ):
        self.name = name
        self.water_type = water_type
        self.enabled_parameter_ids = enabled_parameter_ids
        self.custom_parameters = custom_parameters or []


class TankResponse(TankRequest):
    def __init__(self, id: int, name: str, water_type: str, photo_url: str | None = None):
        super().__init__(name, water_type)
        self.id = id
        self.photo_url = photo_url
