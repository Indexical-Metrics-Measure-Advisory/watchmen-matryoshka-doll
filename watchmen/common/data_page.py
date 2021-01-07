from bson import ObjectId
from pydantic import BaseModel, BaseConfig

from watchmen.common.mongo_model import MongoModel


class DataPage(MongoModel):
    data: list=[];
    itemCount: int=None;
    pageNumber: int=None;
    pageSize: int=None;
    pageCount: int=None;

    # class Config(BaseConfig):
    #     json_encoders = {
    #         # datetime: lambda dt: dt.isoformat(),
    #         ObjectId: lambda oid: str(oid),
    #     }
