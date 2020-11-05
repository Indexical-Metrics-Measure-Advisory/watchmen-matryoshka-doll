from watchmen.storage.engine.storage_engine import get_client
from watchmen.utils.data_utils import WATCHMEN

db = get_client(WATCHMEN)

collection = db.get_collection('mapping_rules')


def load_topic_mapping_rule(model_schema_id, topic_id):
    return collection.find_one(
        {'$and': [{"targetTopicId": topic_id}, {"lakeSchemaId": model_schema_id}]}
    )


def save_topic_mapping_rule(topic_mapping_rule):
    return collection.insert_one(topic_mapping_rule.dict())
