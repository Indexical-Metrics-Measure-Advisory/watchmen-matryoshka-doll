import logging
from datetime import datetime

from watchmen.monitor.model.pipeline_monitor import UnitActionStatus
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


# TODO alert for validation 
def init(action: UnitAction, pipeline_topic: Topic):
    def alarm(raw_data, context):
        unit_action_status = UnitActionStatus()
        unit_action_status.type = action.type
        start_time = datetime.utcnow()

        log.info("alert data")
        # context_target_name = action.targetName
        # topic = get_topic_by_id(action.topicId)
        # factor = get_factor(action.factorId, topic)
        # condition = action.by
        # where_condition = build_right_query(condition, pipeline_topic, raw_data, topic)
        # filter_where_condition = filter_condition(where_condition, 0)
        # target_data = read_topic_data(filter_where_condition, topic.name, condition.mode)
        # # print("target_data :", target_data)
        # # print("factor.name  :", factor.name)
        # if factor.name in target_data:
        #     context[context_target_name] = target_data[factor.name]
        # # print("context :", context)
        time_elapsed = datetime.utcnow() - start_time
        execution_time = time_elapsed.microseconds / 1000
        unit_action_status.complete_time = execution_time
        return context, unit_action_status

    return alarm
