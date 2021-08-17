from datetime import datetime, date

from bson import ObjectId
from pydantic import BaseModel, BaseConfig


class WatchmenModel(BaseModel):
    lastModified: datetime = datetime.now().replace(tzinfo=None)
    createTime: str = None

    class Config(BaseConfig):
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid),
            date: lambda dt: dt.isoformat()
            # Enum : lambda e: e.value()
        }
