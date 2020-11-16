from watchmen.storage.engine.storage_engine import get_client
from watchmen.utils.data_utils import WATCHMEN

db = get_client(WATCHMEN)

collection = db.get_collection('mapping_rules')


def load_topic_mapping_by_id(model_schema_id, topic_id):
    return collection.find_one(
        {'$and': [{"targetTopicId": topic_id}, {"lakeSchemaId": model_schema_id}]}
    )


def load_topic_mapping_by_name(temp_topic_name, topic_name):
    return collection.find_one(
        {'$and': [{"sourceTopicName": temp_topic_name}, {"targetTopicName": topic_name}]}
    )


def save_topic_mapping_rule(topic_mapping_rule):
    return collection.insert_one(topic_mapping_rule.dict())
