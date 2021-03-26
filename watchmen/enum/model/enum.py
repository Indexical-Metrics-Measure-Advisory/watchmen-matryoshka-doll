from typing import List

from watchmen.common.mongo_model import MongoModel


class EnumItem(MongoModel):
    itemId:str = None
    code: str = None
    label: str = None
    parentCode: str = None
    replaceCode: str = None
    enumId:str = None


class Enum(MongoModel):
    enumId: str = None
    name: str = None
    description: str = None
    parentEnumId: str = None
    items: List[EnumItem] = []
