from watchmen.common.watchmen_model import WatchmenModel


class DataPage(WatchmenModel):
    data: list = []
    itemCount: int = None
    pageNumber: int = None
    pageSize: int = None
    pageCount: int = None
