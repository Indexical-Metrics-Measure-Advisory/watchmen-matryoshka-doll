from model.model.pipeline.pipeline import ProcessUnit

from watchmen.monitor.model.pipeline_monitor import UnitRunStatus
from watchmen.pipeline.core.context.stage_context import StageContext


class UnitContext:
    stageContext: StageContext
    unit: ProcessUnit
    unitStatus: UnitRunStatus

    def __init__(self, stageContext, unit, unitStatus=None):
        self.stageContext = stageContext
        self.unit = unit
        self.unitStatus = unitStatus
