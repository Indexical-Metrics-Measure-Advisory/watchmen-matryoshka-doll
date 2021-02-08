from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType

db = get_client()


# @topic_event_trigger
def insert_topic_data(topic_name, mapping_result):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    collection.insert(mapping_result)
    trigger_pipeline(topic_name, mapping_result, TriggerType.insert)


# @topic_event_trigger
def update_topic_data(topic_name, mapping_result, target_data):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    # collection.find_and_modify()
    # TODO find_and_modify
    collection.update_one({"_id": target_data["_id"]}, {"$set": mapping_result})
    data = {**target_data, **mapping_result}
    trigger_pipeline(topic_name, data, TriggerType.update)
