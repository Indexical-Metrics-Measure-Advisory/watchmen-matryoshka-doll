from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.single.stage.unit.utils.units_func import add_audit_columns, add_trace_columns, INSERT, UPDATE

OLD = "old"

NEW = "new"

db = get_client()


# @topic_event_trigger
def insert_topic_data(topic_name, mapping_result, pipeline_uid):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    add_audit_columns(mapping_result, INSERT)
    add_trace_columns(mapping_result, "insert_row", pipeline_uid)
    collection.insert(mapping_result)
    trigger_pipeline(topic_name, {NEW: mapping_result, OLD: None}, TriggerType.insert)


# @topic_event_trigger
def update_topic_data(topic_name, mapping_result, target_data, pipeline_uid):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    old_data = __find_data_by_id(collection, target_data["_id"])
    add_audit_columns(mapping_result, UPDATE)
    add_trace_columns(mapping_result, "update_row", pipeline_uid)
    collection.update_one({"_id": target_data["_id"]}, {"$set": mapping_result})
    data = {**target_data, **mapping_result}
    trigger_pipeline(topic_name, {NEW: data, OLD: old_data}, TriggerType.update)


def find_and_modify_topic_data(topic_name, query, update_data, target_data):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    old_data = __find_data_by_id(collection, target_data["_id"])
    collection.find_and_modify(query=query, update=update_data)
    trigger_pipeline(topic_name, {NEW: update_data, OLD: old_data}, TriggerType.update)


def __find_data_by_id(collection, id):
    result = collection.find_one({"_id": id})
    return result
