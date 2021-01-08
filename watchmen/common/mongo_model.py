from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, BaseConfig


class MongoModel(BaseModel):
    last_modified:datetime = datetime.utcnow()

    class Config(BaseConfig):
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid)
        }
