class TankRequest:
    def __init__(self, name: str):
        self.name = name


class TankResponse(TankRequest):
    def __init__(self, id: int, name: str, photo_url: str | None = None):
        super().__init__(name)
        self.id = id
        self.photo_url = photo_url
