import logging
import re
import time
from typing import Any

from pydantic.main import BaseModel

from watchmen.common.alarm import AlarmMessage
from watchmen.common.constants import pipeline_constants
from watchmen.monitor.model.pipeline_monitor import UnitActionStatus
from watchmen.monitor.services.alarm_service import sync_alarm_message
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import __check_condition, get_source_factor_value
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor_by_name
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


class VariableModel(BaseModel):
    variable: str = None
    value: Any = None
    variableType: str = None


def __find_variable(message):
    return re.findall('{(.+?)}', message)


def __build_message(message, pipeline_topic, raw_data, context):
    variable_list = __find_variable(message)
    variable_results = []
    for variable in variable_list:
        factor = get_factor_by_name(variable, pipeline_topic)
        if variable in context:
            value = context[variable]
            variable_model = VariableModel(variable=variable, value=value, variableType="context")
            variable_results.append(variable_model)
        elif factor:
            value = get_source_factor_value(raw_data, factor)
            variable_model = VariableModel(variable=variable, value=value, variableType="factor")
            variable_results.append(variable_model)
        else:
            variable_model = VariableModel(variable=variable, value=variable, variableType="constants")
            variable_results.append(variable_model)

    for variable_model in variable_results:
        message = message.replace("${" + variable_model.variable + "}", str(variable_model.value))

    return message


def __sync_alarm_message(alarm_message: AlarmMessage):
    sync_alarm_message(alarm_message)


def init(action: UnitAction, pipeline_topic: Topic):
    def alarm(instance, context):
        raw_data, old_value = instance[pipeline_constants.NEW], instance[pipeline_constants.OLD]
        unit_action_status = UnitActionStatus()
        unit_action_status.type = action.type
        start = time.time()
        log.info("alert data")
        match_result = __check_condition(action, pipeline_topic, instance,context)

        if match_result:
            alarm_message = AlarmMessage(severity=action.severity)
            alarm_message.message = __build_message(action.message, pipeline_topic, raw_data, context)
            __sync_alarm_message(alarm_message)

        elapsed_time = time.time() - start
        unit_action_status.complete_time = elapsed_time
        return context, unit_action_status,[]

    return alarm
