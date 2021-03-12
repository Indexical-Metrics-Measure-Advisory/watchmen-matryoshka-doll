from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


class Favorite(MongoModel):
    connectedSpaceIds: list = []
    dashboardIds: list = []
    userId: str = None
