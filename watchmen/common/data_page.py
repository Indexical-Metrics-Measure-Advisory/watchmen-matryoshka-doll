# from watchmen.common.watchmen_model import WatchmenModel
from pydantic import BaseModel


class DataPage(BaseModel):
    data: list = []
    itemCount: int = None
    pageNumber: int = None
    pageSize: int = None
    pageCount: int = None
