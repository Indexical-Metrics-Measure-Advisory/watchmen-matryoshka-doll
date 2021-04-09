from watchmen.common.constants import pipeline_constants
from watchmen.common.storage.storage_template import topic_data_find_by_id, topic_data_update_one, \
    topic_data_insert_one, topic_find_one_and_update
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.single.stage.unit.utils.units_func import add_audit_columns, add_trace_columns, INSERT, UPDATE



def insert_topic_data(topic_name, mapping_result, pipeline_uid):
    """
    collection_name = build_collection_name(topic_name)
    codec_options = build_code_options()
    collection = db.get_collection(collection_name, codec_options=codec_options)
    """
    add_audit_columns(mapping_result, INSERT)
    add_trace_columns(mapping_result, "insert_row", pipeline_uid)
    # collection.insert(mapping_result)
    topic_data_insert_one(mapping_result, topic_name)
    trigger_pipeline(topic_name, {pipeline_constants.NEW: mapping_result, pipeline_constants.OLD: None},
                     TriggerType.insert)


def update_topic_data(topic_name, mapping_result, target_data, pipeline_uid):
    '''
    collection_name = build_collection_name(topic_name)
    codec_options = build_code_options()
    collection = db.get_collection(collection_name, codec_options=codec_options)
    old_data = find_topic_data_by_id(collection, target_data["_id"])
    '''
    old_data = topic_data_find_by_id(target_data["_id"], topic_name)
    add_audit_columns(mapping_result, UPDATE)
    add_trace_columns(mapping_result, "update_row", pipeline_uid)
    '''
    collection.update_one({"_id": target_data["_id"]}, {"$set": mapping_result})
    '''
    topic_data_update_one(target_data["_id"], mapping_result, topic_name)
    data = {**target_data, **mapping_result}
    trigger_pipeline(topic_name, {pipeline_constants.NEW: data, pipeline_constants.OLD: old_data}, TriggerType.update)


def find_and_modify_topic_data(topic_name, query, update_data):
    '''
    collection_name = build_collection_name(topic_name)
    codec_options = build_code_options()
    collection = db.get_collection(collection_name, codec_options=codec_options)
    old_value = collection.find_one_and_update(filter=query, update=update_data, upsert=True)
    '''
    old_value = topic_find_one_and_update(query, update_data, topic_name)
    trigger_pipeline(topic_name, {pipeline_constants.NEW: update_data, pipeline_constants.OLD: old_value},
                     TriggerType.update)
