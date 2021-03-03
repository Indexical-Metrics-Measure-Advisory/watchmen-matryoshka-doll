from pydantic import BaseModel


class LastSnapshot(BaseModel):
    language: str = None
    lastDashboardId: str = None
    favoritePin: bool = False
    userId:str = None
