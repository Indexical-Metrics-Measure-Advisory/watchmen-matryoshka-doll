from watchmen.common.watchmen_model import WatchmenModel


class Favorite(WatchmenModel):
    connectedSpaceIds: list = []
    dashboardIds: list = []
    userId: str = None
