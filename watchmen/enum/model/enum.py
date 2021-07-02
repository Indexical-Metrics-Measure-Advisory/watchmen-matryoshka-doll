from typing import List

from watchmen.common.watchmen_model import WatchmenModel


class EnumItem(WatchmenModel):
    itemId: str = None
    code: str = None
    label: str = None
    parentCode: str = None
    replaceCode: str = None
    enumId: str = None


class Enum(WatchmenModel):
    enumId: str = None
    name: str = None
    description: str = None
    parentEnumId: str = None
    items: List[EnumItem] = []
