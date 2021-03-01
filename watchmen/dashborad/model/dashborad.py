from typing import List, Any

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


class DashboardReport(BaseModel):
    reportId: str = None
    rect: Any = None


class ConsoleDashboard(MongoModel):
    dashboardId: str = None
    name: str = None
    reports: List[DashboardReport] = None
    lastVisitTime: str = None
    userId: str = None
