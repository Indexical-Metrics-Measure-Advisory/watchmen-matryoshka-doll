from datetime import datetime

from watchmen.common.parameter import ParameterJoint, Parameter
from watchmen.monitor.model.pipeline_monitor import UnitStatus
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import run_mapping_rules, \
    get_source_value_list, filter_condition, find_pipeline_topic_condition
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import insert_topic_data, update_topic_data
from watchmen.pipeline.single.stage.unit.utils import PIPELINE_UID
from watchmen.pipeline.single.stage.unit.utils.units_func import get_execute_time, get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


def init(action: UnitAction, pipeline_topic: Topic):
    def merge_or_insert_topic(raw_data, context):

        unit_action_status = UnitStatus()
        unit_action_status.type = action.type
        start_time = datetime.now()
        pipeline_uid = context[PIPELINE_UID]

        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))

        target_topic = get_topic_by_id(action.topicId)

        mapping_results,mapping_logs = run_mapping_rules(action.mapping, target_topic, raw_data, pipeline_topic)

        conditions = action.by

        where_condition = find_pipeline_topic_condition(conditions, pipeline_topic, raw_data, target_topic)

        for index in range(len(mapping_results)):
            filter_where_condition = filter_condition(where_condition, index)

            target_data = read_topic_data(filter_where_condition, target_topic.name, conditions.jointType)
            if target_data is None:
                insert_topic_data(target_topic.name, mapping_results[index],pipeline_uid)
            else:
                update_topic_data(target_topic.name, mapping_results[index], target_data,pipeline_uid)

        unit_action_status.mapping=mapping_logs
        unit_action_status.complete_time = get_execute_time(start_time)
        return context, unit_action_status

    return merge_or_insert_topic
