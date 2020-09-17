import pprint
import string
from enum import Enum

from bson.codec_options import TypeCodec, TypeEncoder
from pymongo import MongoClient

from watchmen.utils.data_utils import RelationshipType

from bson.codec_options import TypeRegistry
from bson.codec_options import CodecOptions
# from bson.son import Decimal128

client = MongoClient('localhost', 27017)
db = client['watchmen']


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


def update_data_schema(data):
    pass


def load_data_schema_by_id(id):
    # collection
    return collection.find_one(id)


def delete_data_schema_by_id(id):
    pass
