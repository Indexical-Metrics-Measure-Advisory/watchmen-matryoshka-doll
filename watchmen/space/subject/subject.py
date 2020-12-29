from pydantic import BaseModel
import typing


class Subject(BaseModel):
    topics: typing.List
    factors: typing.List
    filters: typing.List
    joins: typing.List
