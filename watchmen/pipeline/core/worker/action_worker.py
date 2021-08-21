import importlib
import logging
import traceback
from functools import lru_cache

from watchmen.pipeline.core.context.action_context import ActionContext

PIPELINE_CORE_ACTION_ = "watchmen.pipeline.core.action."

log = logging.getLogger("app." + __name__)


@lru_cache(maxsize=16)
def convert_action_type(action_type: str):
    return action_type.replace("-", "_")


def get_action_func(action):
    action_func = importlib.import_module(PIPELINE_CORE_ACTION_ + convert_action_type(action.type))
    return action_func


def run_action(action_context: ActionContext):
    if action_context.get_current_user() is None:
        raise Exception("run_action currentUser is None")

    action = action_context.action
    action_func = get_action_func(action)
    func = action_func.init(action_context)
    try:
        action_run_status, trigger_pipeline_data_list = func()
        action_context.actionStatus = action_run_status
        return action_context, trigger_pipeline_data_list
    except Exception as e:
        log.error(traceback.format_exc())
        raise e
