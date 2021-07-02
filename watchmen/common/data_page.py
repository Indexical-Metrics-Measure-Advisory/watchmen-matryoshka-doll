from pydantic import BaseModel

from watchmen.common.watchmen_model import WatchmenModel


class DataPage(BaseModel):
    data: list = []
    itemCount: int = None
    pageNumber: int = None
    pageSize: int = None
    pageCount: int = None
