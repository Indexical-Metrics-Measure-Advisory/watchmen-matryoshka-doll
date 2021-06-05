import logging

from watchmen.monitor.model.pipeline_monitor import UnitRunStatus
from watchmen.pipeline.core.context.stage_context import StageContext
from watchmen.pipeline.core.context.unit_context import UnitContext
from watchmen.pipeline.core.worker.unit_worker import run_unit
from watchmen.pipeline.single.stage.unit.mongo.index import __check_condition

log = logging.getLogger("app." + __name__)


def should_run(stageContext: StageContext):
    stage_ = stageContext.stage
    pipeline_topic = stageContext.pipelineContext.pipelineTopic
    data = stageContext.pipelineContext.data
    context = stageContext.pipelineContext.variables
    return __check_condition(stage_, pipeline_topic, data, context)


def run_stage(stageContext: StageContext):
    if should_run(stageContext):
        stage = stageContext.stage
        for unit in stage.units:
            unit_run_status = UnitRunStatus()
            unitContext = UnitContext(stageContext, unit, unit_run_status)
            run_unit(unitContext)
            stageContext.stageStatus.units.append(unitContext.unitStatus)
