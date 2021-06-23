import copy

from watchmen.pipeline.core.context.unit_context import UnitContext


class ActionContext:
    unitContext: UnitContext
    action: any
    previousOfTriggerData: dict = {}
    currentOfTriggerData: dict = {}
    actionStatus: any
    delegateVariableName: str = None
    delegateValue: any = None

    def __init__(self, unitContext, action):
        self.unitContext = unitContext
        self.action = action
        self.previousOfTriggerData = unitContext.stageContext.pipelineContext.previousOfTriggerData
        self.currentOfTriggerData = unitContext.stageContext.pipelineContext.currentOfTriggerData


def get_variables(actionContext: ActionContext) -> dict:
    variables = copy.deepcopy(actionContext.unitContext.stageContext.pipelineContext.variables)
    delegateVariableName = actionContext.delegateVariableName

    delegateValue = actionContext.delegateValue
    if delegateVariableName is not None and delegateVariableName != "":
        variables[delegateVariableName] = delegateValue
    return variables


def set_variable(actionContext: ActionContext, variable_name, variable_value):
    variables = actionContext.unitContext.stageContext.pipelineContext.variables
    variables[variable_name] = variable_value
