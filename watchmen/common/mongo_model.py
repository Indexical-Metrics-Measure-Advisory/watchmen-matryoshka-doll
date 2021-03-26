from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, BaseConfig


class MongoModel(BaseModel):
    lastModified: datetime = datetime.utcnow()
    createTime: str = None

    # lastModifyTime: str = None

    class Config(BaseConfig):
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid)
            # Enum : lambda e: e.value()
        }
