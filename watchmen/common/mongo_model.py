import datetime

from bson import ObjectId
from pydantic import BaseModel, BaseConfig


class MongoModel(BaseModel):
    pageSize: int = None
    pageNumber: int = None

    class Config(BaseConfig):
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid),
        }
