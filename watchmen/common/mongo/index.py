from decimal import Decimal

from bson import Decimal128
from bson.codec_options import TypeCodec, TypeRegistry, CodecOptions

from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name

client = get_client()

collection_list_name = client.list_collection_names()


def check_collection_if_exist(dbname, collection_name):
    return collection_name in collection_list_name


def delete_topic_collection(collection_name):
    topic_name = build_collection_name(collection_name)
    client.get_collection(topic_name).drop()


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
