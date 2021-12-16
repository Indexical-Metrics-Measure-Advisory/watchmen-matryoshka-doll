from model.model.common.watchmen_model import WatchmenModel


class DataSetIndex(WatchmenModel):
    datasetIndexId: str = None
    subjectId:str=None
    topicId:str=None
    factorId:str = None
    columnId:str=None
    columnAlias:str=None
    subjectName:str =None
    tenantId: str = None

