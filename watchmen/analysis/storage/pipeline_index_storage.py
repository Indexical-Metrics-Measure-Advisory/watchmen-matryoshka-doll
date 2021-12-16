from typing import List

from watchmen.analysis.model.pipeline_index import PipelineIndex
from watchmen.database.find_storage_template import find_storage_template

PIPELINE_INDEX = "pipeline_index"

storage_template = find_storage_template()


async def create_pipeline_index(pipeline_index: PipelineIndex):
    return storage_template.insert_one(pipeline_index, PipelineIndex,
                                       PIPELINE_INDEX)


async def update_pipeline_index(pipeline_index: PipelineIndex):
    pass


async def delete_pipeline_index(pipeline_index: PipelineIndex):
    pass


async def load_pipeline_index_list_by_pipeline_id(pipeline_id, current_user) -> List[PipelineIndex]:
    return storage_template.find_({"and": [{"pipelineid": pipeline_id}, {"tenantid": current_user.tenantId}]},
                                  PipelineIndex,
                                  PIPELINE_INDEX)


async def delete_pipeline_index_list_by_pipeline_id(pipeline_id, current_user):
    return storage_template.delete_({"and": [{"pipelineid": pipeline_id}, {"tenantid": current_user.tenantId}]},
                                    PipelineIndex,
                                    PIPELINE_INDEX)
