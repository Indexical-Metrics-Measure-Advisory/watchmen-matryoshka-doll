from bson.codec_options import TypeEncoder, TypeRegistry, CodecOptions

from watchmen.event import event
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN, RelationshipType

db = get_client(WATCHMEN)


class EnumCodec(TypeEncoder):
    python_type = RelationshipType

    def transform_python(self, value):
        # print(value.value)ßß
        return value.value


codec = EnumCodec()
type_registry = TypeRegistry([codec])
codec_options = CodecOptions(type_registry=type_registry)


def build_collection_name(name):
    return "raw_"+name


@event.after
def save_entity_set(entity_set):
    domain_collection = db.get_collection(build_collection_name(entity_set.domain),codec_options=codec_options)
    return domain_collection.insert_one(entity_set.dict())
