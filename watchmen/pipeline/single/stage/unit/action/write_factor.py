import logging
import traceback
from datetime import datetime

from watchmen.monitor.model.pipeline_monitor import UnitStatus, WriteFactorAction
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.pipeline_service import ERROR
from watchmen.pipeline.single.stage.unit.action.insert_or_merge_row import filter_condition
from watchmen.pipeline.single.stage.unit.mongo.index import find_pipeline_topic_condition
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor, get_value, convert_factor_type
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic

IN_MEMORY = "in-memory"

COUNT = "count"

# SUM = "sum"

log = logging.getLogger("app." + __name__)


# TODO refactor write factor

def get_condition_factor_value(raw_data, where_conditions):
    factor_value = {}
    for condition in where_conditions:
        right_factor = condition["right_factor"]
        value = get_value(right_factor, raw_data)

        factor_value[right_factor.name] = value

    return factor_value


# TODO write factor

def init(action: UnitAction, pipeline_topic: Topic):
    def write_factor(raw_data, context):

        unit_action_status = UnitStatus()
        unit_action_status.type = action.type
        start_time = datetime.now()

        action_log = WriteFactorAction()
        try:
            if action.topicId is not None:
                # print("raw_data",raw_data)
                target_topic = get_topic_by_id(action.topicId)

                conditions = action.by

                # some_value = action.value
                where_condition = find_pipeline_topic_condition(conditions, pipeline_topic, raw_data, target_topic)
                # filter_where_condition =
                target_data = read_topic_data(filter_condition(where_condition, 0), target_topic.name,
                                              conditions.jointType)
                target_factor = get_factor(action.factorId, target_topic)

                value = __get_value(raw_data, some_value, context, target_factor)
                # condition_factors = get_condition_factor_value(raw_data, where_condition)
                #
                # if some_value.arithmetic == SUM:
                #     if target_data is None:
                #         insert_data = {**{target_factor.name: value}, **condition_factors}
                #         log.info("Insert data : {0}".format(insert_data))
                #         insert_topic_data(target_topic.name, insert_data)
                #     else:
                #         # print("target_factor.name :",target_factor.name)
                #         if target_factor.name in target_data:
                #             source_value = target_data[target_factor.name]
                #         else:
                #             source_value = 0
                #         value = source_value + value
                #         update_data = {target_factor.name: value}
                #         update_topic_data(target_topic.name, update_data, target_data)
                #
                # elif some_value.arithmetic == COUNT:
                #     if target_data is None:
                #         insert_data = {**{target_factor.name: 1}, **condition_factors}
                #         insert_topic_data(target_topic.name, insert_data)
                #     else:
                #         if target_factor.name in target_data:
                #             source_value = target_data[target_factor.name]
                #         else:
                #             source_value = 0
                #         value = source_value + 1
                #         update_data = {target_factor.name: value}
                #         update_topic_data(target_topic.name, update_data, target_data)
                # else:
                #     if target_data is None:
                #         insert_data = {**{target_factor.name: value}, **condition_factors}
                #         log.debug("Insert data : {0}".format(insert_data))
                #         insert_topic_data(target_topic.name, insert_data)
                #     else:
                #         update_data = {target_factor.name: value}
                #         update_topic_data(target_topic.name, update_data, target_data)
        except Exception as e:
            unit_action_status.status = ERROR
            unit_action_status.error = traceback.format_exc()
            raise e
        time_elapsed = datetime.now() - start_time
        execution_time = time_elapsed.microseconds / 1000
        unit_action_status.complete_time = execution_time
        return context, unit_action_status

    def __get_value(raw_data, some_value, context, target_factor):
        if some_value.type == IN_MEMORY:
            return convert_factor_type(context[some_value.name], target_factor.type)
        else:
            source_factor = get_factor(some_value.factorId, pipeline_topic)
            value = get_value(source_factor, raw_data)
            return value

    return write_factor
