# import json
import logging
import time

from watchmen.pipeline.core.context.action_context import get_variables, ActionContext
from watchmen.pipeline.core.mapping.parse_mapping import parse_mappings
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.storage.write_topic_data import insert_topic_data
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

log = logging.getLogger("app." + __name__)


def init(action_context: ActionContext):
    def insert_topic():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "InsertRow"
        status.uid = action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId

        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData
        action = action_context.action
        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))

        target_topic = get_topic_by_id(action.topicId)
        variables = get_variables(action_context)

        log.info("target_topic name: {0}".format(target_topic.name))
        mappings_results, having_aggregate_functions = parse_mappings(action.mapping,
                                                                      target_topic,
                                                                      previous_data,
                                                                      current_data,
                                                                      variables)
        status.mapping = mappings_results
        trigger_pipeline_data_list = [insert_topic_data(target_topic.name,
                                                        mappings_results,
                                                        action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId
                                                        )]

        status.insertCount = status.insertCount + 1

        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, trigger_pipeline_data_list

    return insert_topic
