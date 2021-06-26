from decimal import Decimal

from bson import Decimal128
from bson.codec_options import TypeCodec, TypeRegistry, CodecOptions

import watchmen

from pymongo import MongoClient
from watchmen.config.config import settings

client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT, username=settings.MONGO_USERNAME,
                     password=settings.MONGO_PASSWORD)


db = client[settings.MONGO_DATABASE]


def get_client():
    return db


def get_client_db():
    return client


def delete_topic_collection(collection_name):
    '''
    topic_name = build_collection_name(collection_name)
    client.get_collection(topic_name).drop()
    '''
    watchmen.common.storage.storage_template.topic_data_delete_(None, collection_name)


class DecimalCodec(TypeCodec):
    python_type = Decimal  # the Python type acted upon by this type codec
    bson_type = Decimal128  # the BSON type acted upon by this type codec

    def transform_python(self, value):
        """Function that transforms a custom type value into a type
        that BSON can encode."""
        return Decimal128(value)

    def transform_bson(self, value):
        """Function that transforms a vanilla BSON type value into our
        custom type."""
        return value.to_decimal()


def build_code_options():
    decimal_codec = DecimalCodec()
    type_registry = TypeRegistry([decimal_codec])
    codec_options = CodecOptions(type_registry=type_registry)
    return codec_options
