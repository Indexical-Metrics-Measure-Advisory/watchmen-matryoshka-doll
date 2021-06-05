from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.storage_template import insert_one, update_one, find_, find_by_id, update_, list_all
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.model.pipeline_graph import PipelinesGraphics

USER_ID = "userId"

PIPELINES = "pipelines"

PIPELINE_GRAPH = "pipeline_graph"


# template = find_template()


def create_pipeline(pipeline: Pipeline) -> Pipeline:
    pipeline.pipelineId = get_surrogate_key()
    # return template.create(PIPELINES, pipeline, Pipeline)
    return insert_one(pipeline, Pipeline, PIPELINES)


def update_pipeline(pipeline: Pipeline) -> Pipeline:
    # load_pipeline_by_topic_id.cache_clear()
    # return template.update_one(PIPELINES, {"pipelineId": pipeline.pipelineId}, pipeline, Pipeline)
    return update_one(pipeline, Pipeline, PIPELINES)


def __convert_to_object(x):
    return Pipeline.parse_obj(x)


# @lru_cache(maxsize=50)
def load_pipeline_by_topic_id(topic_id):
    # return template.find(PIPELINES, {"topicId": topic_id}, Pipeline)
    return find_({"topicId": topic_id}, Pipeline, PIPELINES)


def load_pipeline_by_id(pipeline_id):
    # return template.find_one(PIPELINES, {"pipelineId": pipeline_id}, Pipeline)
    return find_by_id(pipeline_id, Pipeline, PIPELINES)


def update_pipeline_status(pipeline_id, enabled):
    # load_pipeline_by_topic_id.cache_clear()
    # template.update_one(PIPELINES, {"pipelineId": pipeline_id}, {"enabled": enabled}, Pipeline)
    update_({"pipelineId": pipeline_id}, {"enabled": enabled}, Pipeline, PIPELINES)


def update_pipeline_name(pipeline_id, name):
    # load_pipeline_by_topic_id.cache_clear()
    # template.update_one(PIPELINES, {"pipelineId": pipeline_id}, {"name": name}, Pipeline)
    update_({"pipelineId": pipeline_id}, {"name": name}, Pipeline, PIPELINES)


def load_pipeline_list():
    # return template.find_all(PIPELINES, Pipeline)
    return list_all(Pipeline, PIPELINES)


def create_pipeline_graph(pipeline_graph: PipelinesGraphics):
    # return template.create(PIPELINE_GRAPH, pipeline_graph, PipelinesGraphics)
    return insert_one(pipeline_graph, PipelinesGraphics, PIPELINE_GRAPH)


def update_pipeline_graph(pipeline_graph, user_id):
    # return template.update_one(PIPELINE_GRAPH, {USER_ID: user_id}, pipeline_graph, PipelinesGraphics)
    return update_one(pipeline_graph, PipelinesGraphics, PIPELINE_GRAPH)


def load_pipeline_graph(user_id):
    # return template.find_one(PIPELINE_GRAPH, {USER_ID: user_id}, PipelinesGraphics)
    return find_by_id(user_id, PipelinesGraphics, PIPELINE_GRAPH)


def import_pipeline_to_db(pipeline):
    # template.create(PIPELINE_GRAPH, pipeline, Pipeline)
    insert_one(pipeline, Pipeline, PIPELINES)
