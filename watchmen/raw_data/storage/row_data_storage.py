from pydantic import BaseModel
from storage.storage.engine.storage_engine import get_client

db = get_client()


class RawData(BaseModel):
    domain: str
    model_name: str
    body: dict


def build_collection_name(name):
    return "raw_" + name


def insert_row_data(data):
    domain_collection = db.get_collection(build_collection_name(data.domain))
    domain_collection.insert_one(data.dict())


def batch_import_data(data):
    domain_collection = db.get_collection(build_collection_name(data.domain))
    domain_collection.insert_many(data.dict())
