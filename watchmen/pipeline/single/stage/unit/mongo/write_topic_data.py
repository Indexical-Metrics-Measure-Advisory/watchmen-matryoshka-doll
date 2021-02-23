from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.single.stage.unit.utils.units_func import add_audit_columns, add_trace_columns, INSERT, UPDATE

db = get_client()


# @topic_event_trigger
def insert_topic_data(topic_name, mapping_result,pipeline_uid):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    add_audit_columns(mapping_result, INSERT)
    add_trace_columns(mapping_result, "insert_row", pipeline_uid)
    result = collection.insert(mapping_result)
    trigger_pipeline(topic_name, mapping_result, TriggerType.insert)
    return result


# @topic_event_trigger
def update_topic_data(topic_name, mapping_result, target_data,pipeline_uid):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    add_audit_columns(mapping_result, UPDATE)
    add_trace_columns(mapping_result,"update_row", pipeline_uid)
    # collection.find_and_modify()
    # TODO find_and_modify
    collection.update_one({"_id": target_data["_id"]}, {"$set": mapping_result})
    data = {**target_data, **mapping_result}
    trigger_pipeline(topic_name, data, TriggerType.update)


def find_and_modify_topic_data(topic_name, query, update_data):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    collection.find_and_modify(query=query, update=update_data)
