# from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


class LastSnapshot(MongoModel):
    language: str = None
    lastDashboardId: str = None
    adminDashboardId:str = None
    favoritePin: bool = False
    userId: str = None
