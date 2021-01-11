from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import WATCHMEN
from watchmen.pipeline.model.pipeline import Pipeline

from watchmen.common.storage.engine.storage_engine import get_client

db = get_client(WATCHMEN)

pipeline_collection = db.get_collection('pipeline')


def create_pipeline(pipeline:Pipeline) -> Pipeline:
    pipeline.pipelineId=get_surrogate_key()
    print(pipeline)
    pipeline_collection.insert_one(pipeline.dict())
    return pipeline


def update_pipeline(pipeline:Pipeline) -> Pipeline:
    pipeline_collection.update_one({"topicId": pipeline.topicId}, {"$set": pipeline.dict()})
    return pipeline


def load_pipeline_by_topic_id(topic_id):
    result = pipeline_collection.find({"topicId": topic_id})
    return list(result)


