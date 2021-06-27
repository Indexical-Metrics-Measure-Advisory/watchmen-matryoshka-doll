import logging

from watchmen.monitor.model.pipeline_monitor import UnitRunStatus
from watchmen.pipeline.core.context.stage_context import StageContext
from watchmen.pipeline.core.context.unit_context import UnitContext
from watchmen.pipeline.core.parameter.parse_parameter import parse_parameter_joint
from watchmen.pipeline.core.worker.unit_worker import run_unit
from watchmen.pipeline.single.stage.unit.mongo.index import __check_condition

log = logging.getLogger("app." + __name__)


def should_run(stageContext: StageContext) -> bool:
    stage_ = stageContext.stage
    if stage_.on is None:
        return True
    current_data = stageContext.pipelineContext.currentOfTriggerData
    variables = stageContext.pipelineContext.variables
    return parse_parameter_joint(stage_.on, current_data, variables)


def run_stage(stageContext: StageContext):
    if should_run(stageContext):
        stage = stageContext.stage
        for unit in stage.units:
            unit_run_status = UnitRunStatus()
            unitContext = UnitContext(stageContext, unit, unit_run_status)
            run_unit(unitContext)
            stageContext.stageStatus.units.append(unitContext.unitStatus)
