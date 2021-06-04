from pydantic import BaseModel
from typing import List, Any

from watchmen.pipeline.core.dependency.graph.label import Label
from watchmen.pipeline.core.dependency.graph.property import Property


class Node(BaseModel):
    id: str = None
    object_id: str = None
    object_: Any = None
    name: str = None
    labels: List[Label] = None
    properties: List[Property] = None
