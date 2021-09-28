import time

from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import ActionContext, set_variable, get_variables
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.storage.read_topic_data import query_topic_data
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def init(action_context: ActionContext):
    def write_to_external():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "WriteToExternal"
        status.uid = action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId



        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, []

    return write_to_external
