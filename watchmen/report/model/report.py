from enum import Enum
from typing import List

from watchmen.common.mongo_model import MongoModel
from pydantic import BaseModel


class ReportIndicatorArithmetic(str, Enum):
    NONE = 'none'
    COUNT = 'count'
    SUMMARY = 'sum'
    AVERAGE = 'avg'
    MAXIMUM = 'max'
    MINIMUM = 'min'


class ReportIndicator(BaseModel):
    columnId: str = None
    name: str = None
    arithmetic: ReportIndicatorArithmetic = None


class ReportDimension(BaseModel):
    columnId: str = None
    name: str = None


class ReportRect(BaseModel):
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


class ChartType(str, Enum):
    COUNT = 'count'
    BAR = 'bar'
    LINE = 'line'
    SCATTER = 'scatter'
    PIE = 'pie'
    DOUGHNUT = 'doughnut'
    NIGHTINGALE = 'nightingale'
    SUNBURST = 'sunburst'
    TREE = 'tree'
    TREEMAP = 'treemap'
    MAP = 'map'


class Chart(BaseModel):
    type: ChartType = None
    settings: dict = None


class Report(MongoModel):
    reportId: str = None
    name: str = None
    indicators: List[ReportIndicator] = None
    dimensions: List[ReportDimension] = None
    description: str = None
    rect: ReportRect = None
    chart: Chart = None
    lastVisitTime: str = None
