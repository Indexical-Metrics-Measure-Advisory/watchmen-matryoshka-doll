from enum import Enum
from typing import List

from pydantic import BaseModel

from watchmen.pipeline.core.dependency.graph.node import Node
from watchmen.pipeline.core.dependency.graph.property import Property


class Relationship(BaseModel):
    id: str = None
    name: str = None
    direction: str = None
    properties: List[Property] = None
    left: Node = None
    right: Node = None


class Direction(str, Enum):
    one_way = 'one-way'
    two_way = 'two-way'
    no_way = 'no-way'
