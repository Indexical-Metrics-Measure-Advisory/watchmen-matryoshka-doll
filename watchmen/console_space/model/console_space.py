from datetime import datetime
from typing import List

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel
from watchmen.common.parameter import ParameterJoint, Parameter
from watchmen.report.model.report import Report
from watchmen.topic.topic import Topic


class ConsoleSpaceSubjectChartDataSet(BaseModel):
    meta: List[str] = []
    data: list = []


#
# class ConsoleSpaceSubjectDataSetFilter(BaseModel):
#     topicId: str = None
#     factorId: str = None
#     operator: str = None
#     value: str = None
#
#
# class ConsoleSpaceSubjectDataSetFilterJoint(BaseModel):
#     jointType: str = None
#     filters: List[ConsoleSpaceSubjectDataSetFilter] = []


# class ConsoleSpaceSubjectDataSetColumn(BaseModel):
#     topicId: str = None
#     factorId: str = None
#     operator: str = None
#     secondaryTopicId: str = None
#     secondaryFactorId: str = None
#     alias: str = None


class SubjectDataSetJoin(BaseModel):
    topicId: str = None
    factorId: str = None
    secondaryTopicId: str = None
    secondaryFactorId: str = None
    type: str = None


class SubjectDataSetFilter(ParameterJoint):
    pass


class SubjectDataSetFilterJoint(ParameterJoint):
    filters: List[SubjectDataSetFilter]


class SubjectDataSetColumn(BaseModel):
    columnId: str = None
    parameter: Parameter
    alias: str = None


class SubjectDataSet(BaseModel):
    filters: SubjectDataSetFilterJoint
    columns: List[SubjectDataSetColumn] = []
    joins: List[SubjectDataSetJoin] = []


class ConsoleSpaceSubject(MongoModel):
    subjectId: str = None
    name: str = None
    topicCount: int = None
    graphicsCount: int = None
    lastVisitTime: datetime = None
    createdAt: str = None
    reports: List[Report] = []
    reportIds: list = []
    dataset: SubjectDataSet = None


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
    # groups: List[ConsoleSpaceGroup] = []
    subjects: List[ConsoleSpaceSubject] = []
    groupIds: list = []
    subjectIds: list = []
    userId: str = None
    topics: List[Topic] = []
    # topicRelations: List[TopicRelationship] = []
