from typing import List

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


class EnumItem(BaseModel):
    code: str = None
    label: str = None
    parentCode: str = None


class Enum(MongoModel):
    enumId: str = None
    name: str = None
    description: str = None
    parentEnumId: str = None
    items: List[EnumItem] = []
