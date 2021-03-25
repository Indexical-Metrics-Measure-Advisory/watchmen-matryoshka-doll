from decimal import Decimal

from bson import Decimal128

from watchmen.common.constants import pipeline_constants
from watchmen.common.mongo.index import build_code_options
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.single.stage.unit.utils.units_func import add_audit_columns, add_trace_columns, INSERT, UPDATE
from watchmen.topic.storage.topic_data_storage import find_topic_data_by_id
from bson.codec_options import TypeRegistry, TypeCodec
from bson.codec_options import CodecOptions





db = get_client()


# @topic_event_trigger
def insert_topic_data(topic_name, mapping_result, pipeline_uid):
    collection_name = build_collection_name(topic_name)
    codec_options = build_code_options()
    collection = db.get_collection(collection_name,codec_options=codec_options)
    add_audit_columns(mapping_result, INSERT)
    add_trace_columns(mapping_result, "insert_row", pipeline_uid)
    collection.insert(mapping_result)
    trigger_pipeline(topic_name, {pipeline_constants.NEW: mapping_result, pipeline_constants.OLD: None},
                     TriggerType.insert)





# @topic_event_trigger
def update_topic_data(topic_name, mapping_result, target_data, pipeline_uid):
    collection_name = build_collection_name(topic_name)
    codec_options = build_code_options()
    collection = db.get_collection(collection_name,codec_options=codec_options)
    old_data = find_topic_data_by_id(collection, target_data["_id"])
    add_audit_columns(mapping_result, UPDATE)
    add_trace_columns(mapping_result, "update_row", pipeline_uid)
    collection.update_one({"_id": target_data["_id"]}, {"$set": mapping_result})
    data = {**target_data, **mapping_result}
    trigger_pipeline(topic_name, {pipeline_constants.NEW: data, pipeline_constants.OLD: old_data}, TriggerType.update)


def find_and_modify_topic_data(topic_name, query, update_data, target_data):
    collection_name = build_collection_name(topic_name)
    codec_options = build_code_options()
    collection = db.get_collection(collection_name,codec_options=codec_options)
    old_data = find_topic_data_by_id(collection, target_data["_id"])
    collection.find_and_modify(query=query, update=update_data)
    trigger_pipeline(topic_name, {pipeline_constants.NEW: update_data, pipeline_constants.OLD: old_data},
                     TriggerType.update)
