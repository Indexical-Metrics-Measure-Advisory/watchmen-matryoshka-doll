from datetime import datetime
from typing import List, Any

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel
from watchmen.topic.topic import Topic


class ConsoleSpaceSubjectDataSetFilter(BaseModel):
    topicId: str = None
    factorId: str = None
    operator: str = None
    value: str = None


class ConsoleSpaceSubjectDataSetColumn(BaseModel):
    topicId: str = None
    factorId: str = None;


class ConsoleSpaceSubjectDataSetJoin(BaseModel):
    relationId: str = None


class ConsoleDataSet(BaseModel):
    filters: List[ConsoleSpaceSubjectDataSetFilter] = []
    columns: List[ConsoleSpaceSubjectDataSetColumn] = []
    joins: List[ConsoleSpaceSubjectDataSetJoin] = []


class ConsoleSpaceSubjectChartIndicator(BaseModel):
    topicId: str = None
    factorId: str = None
    aggregator: str = None


class ConsoleSpaceSubjectChartDimension(BaseModel):
    topicId: str = None
    factorId: str = None


class ConsoleSpaceSubjectChart(BaseModel):
    chartId: str = None
    name: str = None
    type: str = None
    indicators: List[ConsoleSpaceSubjectChartIndicator] = []
    dimensions: List[ConsoleSpaceSubjectChartDimension] = []
    rect: Any = None
    predefined: bool = False
    colors: Any = None


class ConsoleSpaceSubject(MongoModel):
    subjectId: str = None
    name: str = None
    topicCount: int = None
    graphicsCount: int = None
    lastVisitTime: datetime = None
    createdAt: str = None
    dataset: ConsoleDataSet = None
    graphics: List[ConsoleSpaceSubjectChart] = []


class ConsoleSpaceGroup(MongoModel):
    groupId: str = None
    name: str = None
    subjects: List[ConsoleSpaceSubject] = []
    subjectIds: list = []


class ConsoleSpace(MongoModel):
    spaceId: str = None
    name: str = None
    connectId: str = None
    type: str = None
    lastVisitTime: datetime = None
    groups: List[ConsoleSpaceGroup] = []
    subjects: List[ConsoleSpaceSubject] = []
    groupIds: list = []
    subjectIds: list = []
    userId: str = None
    topics: List[Topic] = []
