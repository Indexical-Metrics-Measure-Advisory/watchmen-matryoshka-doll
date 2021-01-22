from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN
from watchmen.pipeline.model.pipeline import Pipeline

db = get_client(WATCHMEN)

pipeline_collection = db.get_collection('pipeline')


def create_pipeline(pipeline: Pipeline) -> Pipeline:
    pipeline.pipelineId = get_surrogate_key()
    print(pipeline)
    pipeline_collection.insert_one(pipeline.dict())
    return pipeline


def update_pipeline(pipeline: Pipeline) -> Pipeline:
    pipeline_collection.update_one({"topicId": pipeline.topicId}, {"$set": pipeline.dict()})
    return pipeline


def convert_to_object(x):
    return Pipeline.parse_obj(x)


def load_pipeline_by_topic_id(topic_id):
    result = pipeline_collection.find({"topicId": topic_id})
    return list(map(convert_to_object, list(result)))


def load_pipeline_by_id(pipeline_id):
    result =pipeline_collection.find_one({"pipelineId": pipeline_id})
    return Pipeline.parse_obj(result)
