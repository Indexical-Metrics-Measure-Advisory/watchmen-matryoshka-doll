from enum import Enum
from typing import List, Any

from pydantic import BaseModel

from watchmen.common.parameter import ParameterJoint
from watchmen.common.watchmen_model import WatchmenModel


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


class ReportFunnelType(str, Enum):
    NUMERIC = 'numeric',
    DATE = 'date',
    YEAR = 'year',
    HALF_YEAR = 'half-year',
    QUARTER = 'quarter',
    MONTH = 'month',
    HALF_MONTH = 'half-month',
    TEN_DAYS = 'ten-days',
    WEEK_OF_MONTH = 'week-of-month',
    HALF_WEEK = 'half-week',
    DAY_KIND = 'day-kind',
    DAY_OF_WEEK = 'day-of-week',
    HOUR = 'hour',
    HOUR_KIND = 'hour-kind',
    AM_PM = 'am-pm',
    ENUM = 'enum'


class ReportFunnel(BaseModel):
    funnelId: str = None
    columnId: str = None
    type: ReportFunnelType = None
    range: bool = False
    enabled: bool = False
    values: List[str] = None


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
    CUSTOM='customized'


class Chart(BaseModel):
    type: ChartType = None
    settings: dict = None


class Report(WatchmenModel):
    reportId: str = None
    name: str = None
    filters: ParameterJoint = None
    funnels: List[ReportFunnel] = None
    indicators: List[ReportIndicator] = None
    dimensions: List[ReportDimension] = None
    description: str = None
    rect: ReportRect = None
    chart: Chart = None
    createdAt: str = None
    lastVisitTime: str = None
    tenantId: str = None
    # subjectId: str = None
    simulating: bool = False
    simulateData: List[Any] = None
    simulateThumbnail: str = None
