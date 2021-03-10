from functools import lru_cache

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.model.pipeline_graph import PipelinesGraphics

db = get_client()

pipelines = db.get_collection('pipelines')

pipeline_graph_collection = db.get_collection('pipeline_graph')


def create_pipeline(pipeline: Pipeline) -> Pipeline:
    pipeline.pipelineId = get_surrogate_key()
    pipelines.insert_one(pipeline.dict())
    return pipeline


def update_pipeline(pipeline: Pipeline) -> Pipeline:
    load_pipeline_by_topic_id.cache_clear()
    pipelines.update_one({"pipelineId": pipeline.pipelineId}, {"$set": pipeline.dict()})
    return pipeline


def __convert_to_object(x):
    return Pipeline.parse_obj(x)


@lru_cache(maxsize=100)
def load_pipeline_by_topic_id(topic_id):
    result = pipelines.find({"topicId": topic_id})
    return list(map(__convert_to_object, list(result)))


def load_pipeline_by_id(pipeline_id):
    result = pipelines.find_one({"pipelineId": pipeline_id})
    if result is None:
        return  None
    else:
        return Pipeline.parse_obj(result)


def update_pipeline_status(pipeline_id, enabled):
    pipelines.update_one({"pipelineId": pipeline_id}, {"$set": {"enabled": enabled}})


def update_pipeline_name(pipeline_id, name):
    pipelines.update_one({"pipelineId": pipeline_id}, {"$set": {"name": name}})


def load_pipeline_list():
    result = pipelines.find()
    return list(result)


def create_pipeline_graph(pipeline_graph: PipelinesGraphics):
    pipeline_graph_collection.insert(pipeline_graph.dict())
    return PipelinesGraphics.parse_obj(pipeline_graph)


def update_pipeline_graph(pipeline_graph, user_id):
    pipeline_graph_collection.update_one({"user_id": user_id}, {"$set": pipeline_graph.dict()})
    return PipelinesGraphics.parse_obj(pipeline_graph)


def load_pipeline_graph(user_id):
    result = pipeline_graph_collection.find_one({"userId": user_id})
    if result is None:
        return None
    else:
        return PipelinesGraphics.parse_obj(result)


def import_pipeline_to_db(pipeline):
    pipelines.insert_one(pipeline.dict())
