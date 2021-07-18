from watchmen.common.cache.cache_manage import cacheman, PIPELINES_BY_TOPIC_ID, PIPELINE_BY_ID
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.database.storage.storage_template import insert_one, update_one, find_, update_, delete_one, find_one
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.model.pipeline_graph import PipelinesGraphics


USER_ID = "userId"

PIPELINES = "pipelines"

PIPELINE_GRAPH = "pipeline_graph"


def create_pipeline(pipeline: Pipeline) -> Pipeline:
    pipeline.pipelineId = get_surrogate_key()
    return insert_one(pipeline, Pipeline, PIPELINES)


def update_pipeline(pipeline: Pipeline) -> Pipeline:
    result = update_one(pipeline, Pipeline, PIPELINES)
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
        pipelines = find_({"topicId": topic_id}, Pipeline, PIPELINES)
        if pipelines is not None:
            cacheman[PIPELINES_BY_TOPIC_ID].set(topic_id, pipelines)
        return pipelines
    else:
        pipelines = find_({"and": [{"topicId": topic_id}, {"tenantId": current_user.tenantId}]}, Pipeline, PIPELINES)
        if pipelines is not None:
            cacheman[PIPELINES_BY_TOPIC_ID].set(topic_id, pipelines)
        return pipelines


def load_pipeline_by_id(pipeline_id, current_user):
    cached_pipeline = cacheman[PIPELINE_BY_ID].get(pipeline_id)
    if cached_pipeline is not None:
        return cached_pipeline
    result = find_one({"and": [{"pipelineId": pipeline_id}, {"tenantId": current_user.tenantId}]}, Pipeline, PIPELINES)
    if result is not None:
        cacheman[PIPELINE_BY_ID].set(pipeline_id)
    return result


def update_pipeline_status(pipeline_id, enabled):
    update_({"pipelineId": pipeline_id}, {"enabled": enabled}, Pipeline, PIPELINES)
    cacheman[PIPELINE_BY_ID].delete(pipeline_id)
    cacheman[PIPELINES_BY_TOPIC_ID].clear()


def update_pipeline_name(pipeline_id, name):
    update_({"pipelineId": pipeline_id}, {"name": name}, Pipeline, PIPELINES)
    cacheman[PIPELINE_BY_ID].delete(pipeline_id)
    cacheman[PIPELINES_BY_TOPIC_ID].clear()


def load_pipeline_list(current_user):
    return find_({"tenantId": current_user.tenantId}, Pipeline, PIPELINES)


def create_pipeline_graph(pipeline_graph: PipelinesGraphics):
    return insert_one(pipeline_graph, PipelinesGraphics, PIPELINE_GRAPH)


def update_pipeline_graph(pipeline_graph):
    return update_one(pipeline_graph, PipelinesGraphics, PIPELINE_GRAPH)


def remove_pipeline_graph(pipeline_graph_id):
    return delete_one({"pipelineGraphId": pipeline_graph_id}, PIPELINE_GRAPH)


def load_pipeline_graph(user_id, current_user):
    return find_({"and": [{"userId": user_id}, {"tenantId": current_user.tenantId}]}, PipelinesGraphics, PIPELINE_GRAPH)


def import_pipeline_to_db(pipeline):
    insert_one(pipeline, Pipeline, PIPELINES)
