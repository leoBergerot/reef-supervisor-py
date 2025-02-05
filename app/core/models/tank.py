class TankRequest:
    def __init__(self, name: str):
        self.name = name


class TankResponse(TankRequest):
    def __init__(self, id: int, name: str):
        super().__init__(name)
        self.id = id
