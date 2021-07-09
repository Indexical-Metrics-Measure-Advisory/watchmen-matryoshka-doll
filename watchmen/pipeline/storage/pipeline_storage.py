from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.config.config import settings, PROD
from watchmen.database.storage.storage_template import insert_one, update_one, find_, update_, delete_one, find_one
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.model.pipeline_graph import PipelinesGraphics
from cacheout import Cache

USER_ID = "userId"

PIPELINES = "pipelines"

PIPELINE_GRAPH = "pipeline_graph"

cache = Cache()


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
def load_pipeline_by_topic_id(topic_id, current_user=None):
    if topic_id in cache and settings.ENVIRONMENT == PROD:
        return cache.get(topic_id)

    if current_user is None:
        pipeline = find_({"topicId": topic_id}, Pipeline, PIPELINES)
        if pipeline is not None:
            cache.set(topic_id, pipeline)
        return pipeline
    else:
        pipeline = find_({"and": [{"topicId": topic_id}, {"tenantId": current_user.tenantId}]}, Pipeline, PIPELINES)
        if pipeline is not None:
            cache.set(topic_id, pipeline)
        return pipeline


def load_pipeline_by_id(pipeline_id, current_user):
    # return template.find_one(PIPELINES, {"pipelineId": pipeline_id}, Pipeline)
    return find_one({"and": [{"pipelineId": pipeline_id}, {"tenantId": current_user.tenantId}]}, Pipeline, PIPELINES)


def update_pipeline_status(pipeline_id, enabled):
    # load_pipeline_by_topic_id.cache_clear()
    # template.update_one(PIPELINES, {"pipelineId": pipeline_id}, {"enabled": enabled}, Pipeline)
    update_({"pipelineId": pipeline_id}, {"enabled": enabled}, Pipeline, PIPELINES)


def update_pipeline_name(pipeline_id, name):
    # load_pipeline_by_topic_id.cache_clear()
    # template.update_one(PIPELINES, {"pipelineId": pipeline_id}, {"name": name}, Pipeline)
    update_({"pipelineId": pipeline_id}, {"name": name}, Pipeline, PIPELINES)


def load_pipeline_list(current_user):
    # return template.find_all(PIPELINES, Pipeline)
    return find_({"tenantId": current_user.tenantId}, Pipeline, PIPELINES)


def create_pipeline_graph(pipeline_graph: PipelinesGraphics):
    # return template.create(PIPELINE_GRAPH, pipeline_graph, PipelinesGraphics)
    return insert_one(pipeline_graph, PipelinesGraphics, PIPELINE_GRAPH)


def update_pipeline_graph(pipeline_graph):
    # return template.update_one(PIPELINE_GRAPH, {USER_ID: user_id}, pipeline_graph, PipelinesGraphics)
    return update_one(pipeline_graph, PipelinesGraphics, PIPELINE_GRAPH)


def remove_pipeline_graph(pipeline_graph_id):
    return delete_one({"pipelineGraphId": pipeline_graph_id}, PIPELINE_GRAPH)


def load_pipeline_graph(user_id, current_user):
    return find_({"and": [{"userId": user_id}, {"tenantId": current_user.tenantId}]}, PipelinesGraphics, PIPELINE_GRAPH)


# def load_all_pipelines

def import_pipeline_to_db(pipeline):
    # template.create(PIPELINE_GRAPH, pipeline, Pipeline)
    insert_one(pipeline, Pipeline, PIPELINES)
