from model.model.pipeline.pipeline import Pipeline
from model.model.pipeline.pipeline_graph import PipelinesGraphics

from watchmen_boot.cache.cache_manage import cacheman, PIPELINES_BY_TOPIC_ID, PIPELINE_BY_ID
from watchmen_boot.guid.snowflake import get_surrogate_key
from watchmen.database.find_storage_template import find_storage_template

USER_ID = "userId"

PIPELINES = "pipelines"

PIPELINE_GRAPH = "pipeline_graph"

storage_template = find_storage_template()


def create_pipeline(pipeline: Pipeline) -> Pipeline:
    pipeline.pipelineId = get_surrogate_key()
    return storage_template.insert_one(pipeline, Pipeline, PIPELINES)


def update_pipeline(pipeline: Pipeline) -> Pipeline:
    result = storage_template.update_one(pipeline, Pipeline, PIPELINES)
    cacheman[PIPELINE_BY_ID].delete(result.pipelineId)
    cacheman[PIPELINES_BY_TOPIC_ID].delete(result.topicId)
    return result


def __convert_to_object(x):
    return Pipeline.parse_obj(x)


def load_pipeline_by_topic_id(topic_id, current_user=None):
    cached_pipelines = cacheman[PIPELINES_BY_TOPIC_ID].get(topic_id)
    if cached_pipelines is not None:
        return cached_pipelines

    if current_user is None:
        pipelines = storage_template.find_({"topicId": topic_id}, Pipeline, PIPELINES)
        if pipelines is not None:
            cacheman[PIPELINES_BY_TOPIC_ID].set(topic_id, pipelines)
        return pipelines
    else:
        pipelines = storage_template.find_({"and": [{"topicId": topic_id}, {"tenantId": current_user.tenantId}]},
                                           Pipeline, PIPELINES)
        if pipelines is not None:
            cacheman[PIPELINES_BY_TOPIC_ID].set(topic_id, pipelines)
        return pipelines


def load_pipeline_by_id(pipeline_id, current_user):
    cached_pipeline = cacheman[PIPELINE_BY_ID].get(pipeline_id)
    if cached_pipeline is not None:
        return cached_pipeline
    result = storage_template.find_one({"and": [{"pipelineId": pipeline_id}, {"tenantId": current_user.tenantId}]},
                                       Pipeline, PIPELINES)
    if result is not None:
        cacheman[PIPELINE_BY_ID].set(pipeline_id, result)
    return result


def update_pipeline_status(pipeline_id, enabled):
    storage_template.update_({"pipelineId": pipeline_id}, {"enabled": enabled}, Pipeline, PIPELINES)
    cacheman[PIPELINE_BY_ID].delete(pipeline_id)
    cacheman[PIPELINES_BY_TOPIC_ID].clear()


def update_pipeline_name(pipeline_id, name):
    storage_template.update_({"pipelineId": pipeline_id}, {"name": name}, Pipeline, PIPELINES)
    cacheman[PIPELINE_BY_ID].delete(pipeline_id)
    cacheman[PIPELINES_BY_TOPIC_ID].clear()


def load_pipeline_list(current_user):
    return storage_template.find_({"tenantId": current_user.tenantId}, Pipeline, PIPELINES)


def create_pipeline_graph(pipeline_graph: PipelinesGraphics):
    return storage_template.insert_one(pipeline_graph, PipelinesGraphics, PIPELINE_GRAPH)


def update_pipeline_graph(pipeline_graph):
    return storage_template.update_one(pipeline_graph, PipelinesGraphics, PIPELINE_GRAPH)


def remove_pipeline_graph(pipeline_graph_id):
    return storage_template.delete_one({"pipelineGraphId": pipeline_graph_id}, PIPELINE_GRAPH)


def load_pipeline_graph(user_id, current_user):
    return storage_template.find_({"and": [{"userId": user_id}, {"tenantId": current_user.tenantId}]},
                                  PipelinesGraphics, PIPELINE_GRAPH)


def import_pipeline_to_db(pipeline):
    storage_template.insert_one(pipeline, Pipeline, PIPELINES)
    cacheman[PIPELINE_BY_ID].clear()
    cacheman[PIPELINES_BY_TOPIC_ID].clear()
    return pipeline
