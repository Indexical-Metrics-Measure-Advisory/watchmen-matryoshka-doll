# from pydantic import BaseModel

from watchmen.common.watchmen_model import WatchmenModel


class LastSnapshot(WatchmenModel):
    language: str = None
    lastDashboardId: str = None
    adminDashboardId: str = None
    favoritePin: bool = False
    userId: str = None
