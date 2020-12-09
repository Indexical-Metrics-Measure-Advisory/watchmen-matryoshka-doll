from pydantic import BaseModel
from watchmen.space.factor.factor import Factor
from watchmen.space.topic.topic import Topic
from watchmen.space.subject.filter import Filter
from watchmen.space.subject.join import Join
import typing


class Subject(BaseModel):
    topics: typing.List
    factors: typing.List
    filters: typing.List
    joins: typing.List
