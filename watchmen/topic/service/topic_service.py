import logging

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.raw_data.model_schema import ModelSchema
from watchmen.raw_data.model_schema_set import ModelSchemaSet
from watchmen.topic.factor.factor import Factor
from watchmen.topic.storage.topic_schema_storage import save_topic, update_topic
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


template = find_template()




def create_topic_schema(topic):
    if topic.topicId is None or check_fake_id(topic.topicId):
        topic.topicId = get_surrogate_key()
    if type(topic) is not dict:
        topic = topic.dict()
    save_topic(topic)

    return Topic.parse_obj(topic)


def update_topic_schema(
        topic_id,
        topic: Topic):
    if type(topic) is not dict:
        topic = topic.dict()
    update_topic(topic_id, topic)
    return Topic.parse_obj(topic)


def build_topic(model_schema_set: ModelSchemaSet):
    topic = Topic()
    topic.topicId = get_surrogate_key()
    topic.name = model_schema_set.code
    topic.type = "raw"
    topic.factors = []
    parent = ""
    build_factors(topic.factors, parent, model_schema_set.schemas[topic.name], model_schema_set)
    create_topic_schema(topic)


def build_factors(factors: list, parent: str, model_schema: ModelSchema, model_schema_set: ModelSchemaSet):
    for key, value in model_schema.businessFields.items():
        if value.type == "array" or value.type == "dict":
            if parent == "":
                parent = key
            else:
                parent = parent + "." + key
            build_factors(factors, parent, model_schema_set.schemas[key], model_schema_set)
        else:
            factor = Factor()
            if parent != "":
                factor.name = parent + "." + key
            else:
                factor.name = key
            factor.type = value.type
            factor.factorId = get_surrogate_key()
            factor.label = factor.name
            factors.append(factor)
