import logging
from datetime import datetime

from watchmen.monitor.model.pipeline_monitor import UnitStatus, WriteFactorAction
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.action.insert_or_merge_row import filter_condition
from watchmen.pipeline.single.stage.unit.mongo.index import find_pipeline_topic_condition, get_source_value_list, \
    build_mongo_condition, run_arithmetic_value_list
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import find_and_modify_topic_data, insert_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor, get_value, get_execute_time
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


log = logging.getLogger("app." + __name__)


# TODO refactor write factor

def get_condition_factor_value(raw_data, where_conditions):
    factor_value = {}
    for condition in where_conditions:
        source_factor = condition["source_factor"]
        value = get_value(source_factor, raw_data)

        factor_value[source_factor.name] = value

    return factor_value


def init(action: UnitAction, pipeline_topic: Topic):
    def write_factor(raw_data, context):

        unit_action_status = UnitStatus()
        unit_action_status.type = action.type
        start_time = datetime.now()
        # TODO  action_log
        action_log = WriteFactorAction()

        if action.topicId is not None:

            target_topic = get_topic_by_id(action.topicId)

            conditions = action.by

            where_condition = find_pipeline_topic_condition(conditions, pipeline_topic, raw_data, target_topic)
            filter_where_condition = filter_condition(where_condition)
            target_factor = get_factor(action.factorId, target_topic)

            source_value_list = run_arithmetic_value_list(action.arithmetic,
                                                          get_source_value_list(pipeline_topic, raw_data, [],
                                                                                action.source))
            update_data = {target_factor.name: source_value_list}

            target_data = read_topic_data(filter_where_condition, target_topic.name,
                                          conditions.jointType)

            if target_data is None:
                condition_factors = get_condition_factor_value(raw_data, where_condition)
                insert_data = {**{target_factor.name: source_value_list}, **condition_factors}
                log.info("Insert data : {0}".format(insert_data))
                insert_topic_data(target_topic.name, insert_data)
                pass
            else:
                find_and_modify_topic_data(build_mongo_condition(filter_where_condition, conditions.jointType),
                                           update_data)

        unit_action_status.complete_time = get_execute_time(start_time)
        return context, unit_action_status

    return write_factor
