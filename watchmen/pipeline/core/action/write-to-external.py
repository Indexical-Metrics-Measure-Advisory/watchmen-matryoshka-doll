import time

from watchmen.config.config import settings
from watchmen.external.storage import external_storage
from watchmen.pipeline.core.context.action_context import ActionContext
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus


def init(action_context: ActionContext):
    def write_to_external():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "WriteToExternal"
        status.uid = action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId
        action = action_context.action
        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData
        if settings.EXTERNAL_WRITER_ON:
            external_writer = external_storage.load_external_writer_by_id(action.externalWriterId)

        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, []

    return write_to_external
