import typing

from pydantic import BaseModel


class Subject(BaseModel):
    topics: typing.List
    factors: typing.List
    filters: typing.List
    joins: typing.List
