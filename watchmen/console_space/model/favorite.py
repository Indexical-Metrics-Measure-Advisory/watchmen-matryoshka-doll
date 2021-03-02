from pydantic import BaseModel


class Favorite(BaseModel):
    connectedSpaceIds: list = []
    dashboardIds: list = []
    userId: str = None
