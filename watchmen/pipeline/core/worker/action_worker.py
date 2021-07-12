import importlib
import logging
import time
from functools import lru_cache

PIPELINE_CORE_ACTION_ = "watchmen.pipeline.core.action."

log = logging.getLogger("app." + __name__)


@lru_cache(maxsize=16)
def convert_action_type(action_type: str):
    return action_type.replace("-", "_")


def get_action_func(action):
    stage_method = importlib.import_module(PIPELINE_CORE_ACTION_ + convert_action_type(action.type))
    return stage_method


def run_action(action_context):
    action = action_context.action
    stage_method = get_action_func(action)
    func = stage_method.init(action_context)
    action_run_status, trigger_pipeline_data_list = func()
    action_context.actionStatus = action_run_status
    return action_context, trigger_pipeline_data_list
