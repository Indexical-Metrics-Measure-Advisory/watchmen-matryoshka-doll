from watchmen.monitor.model.pipeline_monitor import StageRunStatus
from watchmen.pipeline.core.context.pipeline_context import PipelineContext
from watchmen.pipeline.model.pipeline import Stage


class StageContext:
    pipelineContext: PipelineContext
    stage: Stage
    stageStatus: StageRunStatus

    def __init__(self, pipelineContext, stage, stageStatus):
        self.pipelineContext = pipelineContext
        self.stage = stage
        self.stageStatus = stageStatus
