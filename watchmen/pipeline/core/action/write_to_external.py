import asyncio
import logging
import time

from watchmen.config.config import settings
from watchmen.external.service.index import get_writer_func
from watchmen.external.storage import external_storage
from watchmen.pipeline.core.context.action_context import ActionContext
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus

log = logging.getLogger("app." + __name__)


def init(action_context: ActionContext):
    def write_to_external():
        # begin time
        start = time.time()

        status = ActionStatus()
        topic = action_context.get_pipeline_context().pipelineTopic
        status.type = "WriteToExternal"
        status.uid = action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId
        action = action_context.action
        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData
        if settings.EXTERNAL_WRITER_ON:
            external_writer = external_storage.load_external_writer_by_id(action.externalWriterId)
            if external_writer:
                writer = get_writer_func(external_writer, topic)
                asyncio.ensure_future(writer(action.eventCode,current_data))
        else:
            log.info(f"EXTERNAL_WRITER_ON  value is {settings.EXTERNAL_WRITER_ON}")
        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, []

    return write_to_external
