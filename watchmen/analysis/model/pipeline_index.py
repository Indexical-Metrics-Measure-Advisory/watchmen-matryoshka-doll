from model.model.common.watchmen_model import WatchmenModel


class PipelineIndex(WatchmenModel):
    pipelineIndexId: str = None
    factorId: str = None
    topicId: str = None
    refType: str = None
    pipelineId: str = None
    pipelineName: str = None
    tenantId: str = None
    stageId: str = None
    stageName: str = None
    unitId: str = None
    unitName: str = None
    actionId: str = None
    mappingToFactorId: str = None
    mappingToTopicId: str = None
    sourceFromFactorId: str = None
    sourceFromTopicId: str = None
