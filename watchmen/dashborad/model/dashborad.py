from datetime import datetime
from typing import List, Any

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


class ConsoleDashboardChart(BaseModel):
    spaceId: str = None
    connectId: str = None
    subjectId: str = None
    chartId: str = None
    rect: Any = None


class ConsoleDashboard(MongoModel):
    dashboardId: str = None
    name: str = None
    lastVisitTime: datetime = None
    current: bool = None
    userId: str = None
    graphics: List[ConsoleDashboardChart] = []
