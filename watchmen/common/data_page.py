from watchmen.common.mongo_model import MongoModel


class DataPage(MongoModel):
    data: list = []
    itemCount: int = None
    pageNumber: int = None
    pageSize: int = None
    pageCount: int = None
