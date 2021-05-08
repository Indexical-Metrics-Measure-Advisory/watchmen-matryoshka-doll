from watchmen.common.constants import pipeline_constants
from watchmen.common.oracle.oracle_template import topic_data_update_
from watchmen.common.storage.storage_template import topic_data_find_by_id, topic_data_update_one, \
    topic_data_insert_one, topic_find_one_and_update
from watchmen.config.config import settings
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.single.stage.unit.model.trigger_data import TriggerData
from watchmen.pipeline.single.stage.unit.utils.units_func import add_audit_columns, add_trace_columns, INSERT, UPDATE


def __build_trigger_pipeline_data(topic_name: str, data, trigger_type):
    return TriggerData(topicName=topic_name, triggerType=trigger_type, data=data)


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
    # trigger_pipeline(topic_name, {pipeline_constants.NEW: mapping_result, pipeline_constants.OLD: None},
    #                  TriggerType.insert)

    return __build_trigger_pipeline_data(topic_name,
                                         {pipeline_constants.NEW: mapping_result, pipeline_constants.OLD: None},
                                         TriggerType.insert)


def __get_key():
    if settings.STORAGE_ENGINE == "mongo":
        return "_id"
    elif settings.STORAGE_ENGINE == "oracle":
        return "id_"


def update_topic_data(topic_name, mapping_result, target_data, pipeline_uid,mongo_query):
    '''
    collection_name = build_collection_name(topic_name)
    codec_options = build_code_options()
    collection = db.get_collection(collection_name, codec_options=codec_options)
    old_data = find_topic_data_by_id(collection, target_data["_id"])
    '''
    old_data = topic_data_find_by_id(target_data[__get_key()], topic_name)
    add_audit_columns(mapping_result, UPDATE)
    add_trace_columns(mapping_result, "update_row", pipeline_uid)
    '''
    collection.update_one({"_id": target_data["_id"]}, {"$set": mapping_result})
    '''

    # update_data = {**old_data,**mapping_result}
    topic_data_update_(topic_name, mongo_query, mapping_result)
    data = {**target_data, **mapping_result}

    return __build_trigger_pipeline_data(topic_name,
                                         {pipeline_constants.NEW: data, pipeline_constants.OLD: old_data},
                                         TriggerType.update)


def find_and_modify_topic_data(topic_name, query, update_data, target_data):
    '''
    collection_name = build_collection_name(topic_name)
    codec_options = build_code_options()
    collection = db.get_collection(collection_name, codec_options=codec_options)
    old_value = collection.find_one_and_update(filter=query, update=update_data, upsert=True)
    '''

    if target_data is not None:
        old_data = topic_data_find_by_id(target_data[__get_key()], topic_name)
    else:
        old_data = None

    new_data = topic_find_one_and_update(query, update_data, topic_name)
    return __build_trigger_pipeline_data(topic_name,
                                         {pipeline_constants.NEW: new_data, pipeline_constants.OLD: old_data},
                                         TriggerType.insert if old_data is None else TriggerType.update)
