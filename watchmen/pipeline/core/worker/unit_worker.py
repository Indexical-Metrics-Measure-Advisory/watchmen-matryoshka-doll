import logging

from distributed import as_completed

from watchmen.common.dask.client import DaskClient
from watchmen.config.config import settings
from watchmen.monitor.model.pipeline_monitor import UnitRunStatus
from watchmen.pipeline.core.context.action_context import ActionContext
from watchmen.pipeline.core.context.unit_context import UnitContext
from watchmen.pipeline.core.parameter.parse_parameter import parse_parameter_joint
from watchmen.pipeline.core.worker.action_worker import run_action

log = logging.getLogger("app." + __name__)


def should_run(unit_context: UnitContext, unit_run_status: UnitRunStatus) -> bool:
    unit = unit_context.unit
    if unit.on is None:
        unit_run_status.conditionResult = True
        return True
    current_data = unit_context.stageContext.pipelineContext.currentOfTriggerData
    variables = unit_context.stageContext.pipelineContext.variables
    condition_result = parse_parameter_joint(unit.on, current_data, variables)
    unit_run_status.conditionResult = condition_result
    return condition_result


def run_unit(unit_context: UnitContext):
    if unit_context.unit.do is not None:
        if should_run(unit_context, unit_context.unitStatus):
            unit_context.unitStatus.unitId = unit_context.unit.unitId
            unit_context.unitStatus.name = unit_context.unit.name
            loop_variable_name = unit_context.unit.loopVariableName
            if loop_variable_name is not None and loop_variable_name != "":

                loop_variable = unit_context.stageContext.pipelineContext.variables[loop_variable_name]
                if isinstance(loop_variable, list):
                    if settings.DASK_ON:
                        results, triggers = run_actions(unit_context,
                                                        loop_variable_name,
                                                        None,
                                                        True,
                                                        True)
                    else:
                        results, triggers = run_actions(unit_context,
                                                        loop_variable_name,
                                                        None,
                                                        True,
                                                        False)
                else:
                    raise ValueError(
                        "the value type of loop variable \"{0}\" must be list, now the value is \"{1}\" ".format(
                            loop_variable_name, loop_variable))


            else:
                results, triggers = run_actions(unit_context, None, None, False, False)

            if triggers:
                unit_context.stageContext.pipelineContext.pipeline_trigger_merge_list = [
                    *unit_context.stageContext.pipelineContext.pipeline_trigger_merge_list,
                    *triggers]
            if results:
                for result in results:
                    unit_context.unitStatus.actions.append(result.actionStatus)


def run_actions(unit_context, loop_variable_name=None, loop_variable_value=None, in_loop=None, on_dask=None):
    results = []
    triggers = []
    if in_loop:
        if on_dask:
            futures = []
            client = DaskClient().get_dask_client()
            for value in unit_context.stageContext.pipelineContext.variables[loop_variable_name]:
                futures.append(
                    client.submit(run_actions, unit_context, loop_variable_name, value, False, False, pure=False))
            for future in as_completed(futures):
                result, trigger_pipeline_data_list = future.result()
                results.extend(result)
                triggers.extend(trigger_pipeline_data_list)
        else:
            for value in unit_context.stageContext.pipelineContext.variables[loop_variable_name]:
                result, trigger_pipeline_data_list = run_actions(unit_context, loop_variable_name, value, False, False)
                results.extend(result)
                triggers.extend(trigger_pipeline_data_list)
    else:
        for action in unit_context.unit.do:
            action_context = ActionContext(unit_context, action)
            if loop_variable_name and loop_variable_value:
                action_context.delegateVariableName = loop_variable_name
                action_context.delegateValue = loop_variable_value
            result, trigger_pipeline_data_list = run_action(action_context)
            results.append(result)
            triggers.extend(trigger_pipeline_data_list)
    return results, triggers
