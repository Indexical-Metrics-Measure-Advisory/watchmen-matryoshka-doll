import logging

from watchmen.monitor.model.pipeline_monitor import UnitRunStatus, StageRunStatus
from watchmen.pipeline.core.context.stage_context import StageContext
from watchmen.pipeline.core.context.unit_context import UnitContext
from watchmen.pipeline.core.parameter.parse_parameter import parse_parameter_joint
from watchmen.pipeline.core.worker.unit_worker import run_unit

log = logging.getLogger("app." + __name__)


def should_run(stage_context: StageContext, stage_run_status: StageRunStatus = None) -> bool:
    stage_ = stage_context.stage
    if stage_.on is None:
        stage_run_status.conditionResult = True
        return True
    current_data = stage_context.pipelineContext.currentOfTriggerData
    variables = stage_context.pipelineContext.variables
    condition_result = parse_parameter_joint(stage_.on, current_data, variables)
    stage_run_status.conditionResult = condition_result
    return condition_result


def run_stage(stage_context: StageContext, stage_run_status=None):
    if should_run(stage_context, stage_run_status):
        stage = stage_context.stage
        for unit in stage.units:
            unit_run_status = UnitRunStatus()
            unit_run_status.name = unit.name
            unit_context = UnitContext(stage_context, unit, unit_run_status)
            run_unit(unit_context,unit_run_status)
            stage_context.stageStatus.units.append(unit_context.unitStatus)
