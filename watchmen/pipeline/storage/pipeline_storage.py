from functools import lru_cache

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.model.pipeline_graph import PipelinesGraphics

PIPELINES = "pipelines"

PIPELINE_GRAPH = "pipeline_graph"

# db = get_client()
#
# pipelines = db.get_collection('pipelines')
#
# pipeline_graph_collection = db.get_collection('pipeline_graph')

template = find_template()


def create_pipeline(pipeline: Pipeline) -> Pipeline:
    pipeline.pipelineId = get_surrogate_key()
    # pipelines.insert_one(pipeline.dict())
    # return pipeline
    return template.create(PIPELINES,pipeline,Pipeline)


def update_pipeline(pipeline: Pipeline) -> Pipeline:
    load_pipeline_by_topic_id.cache_clear()
    # pipelines.update_one({"pipelineId": pipeline.pipelineId}, {"$set": pipeline.dict()})
    # return pipeline
    return template.update_one(PIPELINES,{"pipelineId": pipeline.pipelineId},pipeline,Pipeline)


def __convert_to_object(x):
    return Pipeline.parse_obj(x)


@lru_cache(maxsize=50)
def load_pipeline_by_topic_id(topic_id):
    # result = pipelines.find({"topicId": topic_id})
    # return list(map(__convert_to_object, list(result)))
    return template.find(PIPELINES,{"topicId": topic_id},Pipeline)


def load_pipeline_by_id(pipeline_id):
    # result = pipelines.find_one({"pipelineId": pipeline_id})
    # if result is None:
    #     return None
    # else:
    #     return Pipeline.parse_obj(result)
    return template.find_one(PIPELINES,{"pipelineId": pipeline_id},Pipeline)


def update_pipeline_status(pipeline_id, enabled):
    # pipelines.update_one({"pipelineId": pipeline_id}, {"$set": {"enabled": enabled}})
    template.update_one(PIPELINES,{"pipelineId": pipeline_id},{"enabled": enabled},Pipeline)


def update_pipeline_name(pipeline_id, name):
    # pipelines.update_one({"pipelineId": pipeline_id}, {"$set": {"name": name}})
    template.update_one(PIPELINES, {"pipelineId": pipeline_id}, {"name": name}, Pipeline)


def load_pipeline_list():
    # result = pipelines.find()
    # return list(result)
    return template.find_all(PIPELINES,Pipeline)


def create_pipeline_graph(pipeline_graph: PipelinesGraphics):
    # pipeline_graph_collection.insert(pipeline_graph.dict())
    # return PipelinesGraphics.parse_obj(pipeline_graph)
    return template.create(PIPELINE_GRAPH,pipeline_graph,PipelinesGraphics)


def update_pipeline_graph(pipeline_graph, user_id):
    # pipeline_graph_collection.update_one({"user_id": user_id}, {"$set": pipeline_graph.dict()})
    # return PipelinesGraphics.parse_obj(pipeline_graph)
    return template.update_one(PIPELINE_GRAPH,{"user_id": user_id},pipeline_graph,PipelinesGraphics)


def load_pipeline_graph(user_id):
    # result = pipeline_graph_collection.find_one({"userId": user_id})
    # if result is None:
    #     return None
    # else:
    #     return PipelinesGraphics.parse_obj(result)
    return template.find_one(PIPELINE_GRAPH,{"userId": user_id},PipelinesGraphics)


def import_pipeline_to_db(pipeline):
    # pipelines.insert_one(pipeline.dict())
    template.create(PIPELINE_GRAPH,pipeline,Pipeline)
