import logging

from fastapi import APIRouter, Depends

from watchmen.common.model.user import User
from watchmen.common import deps
from watchmen.common.cache.cache_manage import cacheman, TOPIC_BY_NAME, TOPIC_BY_ID, PIPELINE_BY_ID, \
    PIPELINES_BY_TOPIC_ID, COLUMNS_BY_TABLE_NAME, TOPIC_DICT_BY_NAME
from watchmen.database.storage.storage_template import clear_metadata

router = APIRouter()

log = logging.getLogger("app." + __name__)


@router.get("/cache/clear/all", tags=["admin"])
def clear_all():
    cacheman.clear_all()
    clear_metadata()


'''
@router.get("/cache/delete/topic", tags=["admin"])
def delete_topic_cache(topic_name, current_user: User = Depends(deps.get_current_user)):
    cacheman[TOPIC_BY_NAME].delete(topic_name)
'''


@router.get("/cache/clear/topics", tags=["admin"])
def clear_topics_cache(current_user: User = Depends(deps.get_current_user)):
    cacheman[TOPIC_BY_NAME].clear()
    cacheman[TOPIC_DICT_BY_NAME].clear()
    cacheman[TOPIC_BY_ID].clear()
    cacheman[COLUMNS_BY_TABLE_NAME].clear()


'''
@router.get("/cache/delete/pipeline", tags=["admin"])
def delete_pipeline_cache(pipeline_id, current_user: User = Depends(deps.get_current_user)):
    cacheman[PIPELINE_BY_ID].delete(pipeline_id)


@router.get("/cache/delete/topic/pipelines", tags=["admin"])
def clear_pipelines_cache(topic_id, current_user: User = Depends(deps.get_current_user)):
    cacheman[PIPELINES_BY_TOPIC_ID].delete(topic_id)
'''


@router.get("/cache/clear/topics/pipelines", tags=["admin"])
def clear_pipelines_cache(current_user: User = Depends(deps.get_current_user)):
    cacheman[PIPELINES_BY_TOPIC_ID].clear()
    cacheman[PIPELINE_BY_ID].clear()


'''
@router.get("/cache/delete/columns", tags=["admin"])
def delete_table_columns_cache(table_name, current_user: User = Depends(deps.get_current_user)):
    cacheman[COLUMNS_BY_TABLE_NAME].delete(table_name)


@router.get("/cache/clear/columns", tags=["admin"])
def clear_all_table_columns_cache(table_name, current_user: User = Depends(deps.get_current_user)):
    cacheman[COLUMNS_BY_TABLE_NAME].clear()
'''
