import logging
from typing import List

from fastapi import APIRouter, Depends
from model.model.common.user import User
from model.model.topic.topic import Topic

from watchmen.analysis.storage import factor_index_storage
from watchmen.common import deps
from watchmen.topic.storage.topic_schema_storage import get_topic_list_by_ids

router = APIRouter()

log = logging.getLogger("app." + __name__)


@router.get("/query/topic/factor/index", tags=["index"], response_model=List[Topic])
async def load_topic_by_factor_index(query_name: str, current_user: User = Depends(deps.get_current_user)):
    factor_index_list = factor_index_storage.load_factor_index_by_factor_name(query_name, current_user.tenantId)
    topic_factor_index_list = factor_index_storage.load_factor_index_by_topic_name(query_name, current_user.tenantId)
    all_list = factor_index_list + topic_factor_index_list
    topic_id_list = []

    # print(all_list)
    for factor_index in all_list:
        if factor_index.topicId not in topic_id_list:
            topic_id_list.append(factor_index.topicId)
    #
    # print(topic_id_list)
    if topic_id_list:
        result = get_topic_list_by_ids(topic_id_list, current_user)
        print(result)
        return result
    else:
        return []


@router.get("/factor/build/index", tags=["index"])
async def build_factor_index(topic_id=None,current_user:User = Depends(deps.get_current_user)):
    if topic_id is None:
        pass ## build
    else:
        pass ## build pne



@router.get("/pipeline/build/index", tags=["index"])
async def build_pipeline_index(pipeline_id=None,current_user:User = Depends(deps.get_current_user)):
    if pipeline_id is None:
        pass ## build
    else:
        pass ## build pne




