from functools import lru_cache

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.model.pipeline_graph import PipelinesGraphics

PIPELINES = "pipelines"

PIPELINE_GRAPH = "pipeline_graph"

template = find_template()


def create_pipeline(pipeline: Pipeline) -> Pipeline:
    pipeline.pipelineId = get_surrogate_key()
    return template.create(PIPELINES, pipeline, Pipeline)


def update_pipeline(pipeline: Pipeline) -> Pipeline:
    load_pipeline_by_topic_id.cache_clear()
    return template.update_one(PIPELINES, {"pipelineId": pipeline.pipelineId}, pipeline, Pipeline)


def __convert_to_object(x):
    return Pipeline.parse_obj(x)


@lru_cache(maxsize=50)
def load_pipeline_by_topic_id(topic_id):
    return template.find(PIPELINES, {"topicId": topic_id}, Pipeline)


def load_pipeline_by_id(pipeline_id):
    return template.find_one(PIPELINES, {"pipelineId": pipeline_id}, Pipeline)


def update_pipeline_status(pipeline_id, enabled):
    load_pipeline_by_topic_id.cache_clear()
    template.update_one(PIPELINES, {"pipelineId": pipeline_id}, {"enabled": enabled}, Pipeline)


def update_pipeline_name(pipeline_id, name):
    load_pipeline_by_topic_id.cache_clear()
    template.update_one(PIPELINES, {"pipelineId": pipeline_id}, {"name": name}, Pipeline)


def load_pipeline_list():
    return template.find_all(PIPELINES, Pipeline)


def create_pipeline_graph(pipeline_graph: PipelinesGraphics):
    return template.create(PIPELINE_GRAPH, pipeline_graph, PipelinesGraphics)


def update_pipeline_graph(pipeline_graph, user_id):
    return template.update_one(PIPELINE_GRAPH, {"userId": user_id}, pipeline_graph, PipelinesGraphics)


def load_pipeline_graph(user_id):
    return template.find_one(PIPELINE_GRAPH, {"userId": user_id}, PipelinesGraphics)


def import_pipeline_to_db(pipeline):
    template.create(PIPELINE_GRAPH, pipeline, Pipeline)
