from bson.codec_options import CodecOptions
from bson.codec_options import TypeEncoder
from bson.codec_options import TypeRegistry
from pymongo import MongoClient

from watchmen.storage.engine.storage_engine import get_client
from watchmen.utils.data_utils import RelationshipType


# client = MongoClient('localhost', 27017)
# db = client['watchmen']

db = get_client("watchmen")


class EnumCodec(TypeEncoder):
    python_type = RelationshipType

    def transform_python(self, value):
        # print(value.value)
        return value.value


codec = EnumCodec()
type_registry = TypeRegistry([codec])
codec_options = CodecOptions(type_registry=type_registry)
collection = db.get_collection('data_schema', codec_options=codec_options)


def insert_data_schema(data):
    return collection.insert_one(data)


def update_data_schema(id, data):
    return collection.update_one({"_id": id}, {"$set": data})


def load_data_schema_by_id(id):
    # collection
    return collection.find_one(id)


def delete_data_schema_by_id(id):
    return collection.delete_one({"_id": id})
