import logging
import time

from watchmen.pipeline.core.context.action_context import ActionContext
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus

log = logging.getLogger("app." + __name__)


def init(action_context: ActionContext):
    def alarm():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "Alarm"
        status.uid = action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId

        # todo
        log.info("need to do, alarm action")

        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, []

    return alarm
