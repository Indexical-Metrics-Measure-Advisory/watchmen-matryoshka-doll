from typing import List

from watchmen.common.mongo_model import MongoModel


class Report(MongoModel):
    name: str = None
    question: str = None
    alias: List[str] = None
    filters: List[str] = None
    layouts: List[str] = None
