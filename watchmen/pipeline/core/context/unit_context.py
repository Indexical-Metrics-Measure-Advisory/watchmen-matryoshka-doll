
from watchmen.monitor.model.pipeline_monitor import UnitRunStatus
from watchmen.pipeline.core.context.stage_context import StageContext
from watchmen.pipeline.model.pipeline import ProcessUnit


class UnitContext:
    stageContext: StageContext
    unit: ProcessUnit
    unitStatus: UnitRunStatus

    def __init__(self, stageContext, unit, unitStatus):
        self.stageContext = stageContext
        self.unit = unit
        self.unitStatus = unitStatus

