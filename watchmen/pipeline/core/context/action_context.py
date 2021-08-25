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

    def __init__(self, unit_context, action):
        self.unitContext = unit_context
        self.action = action
        self.previousOfTriggerData = unit_context.stageContext.pipelineContext.previousOfTriggerData
        self.currentOfTriggerData = unit_context.stageContext.pipelineContext.currentOfTriggerData

    def get_current_user(self):
        return self.unitContext.stageContext.pipelineContext.currentUser

    def get_pipeline_id(self):
        return self.unitContext.stageContext.pipelineContext.pipeline.pipelineId

    def get_pipeline_context(self):
        return self.unitContext.stageContext.pipelineContext


def get_variables(action_context: ActionContext) -> dict:
    variables = copy.deepcopy(action_context.unitContext.stageContext.pipelineContext.variables)
    delegate_variable_name = action_context.delegateVariableName

    delegate_value = action_context.delegateValue
    if delegate_variable_name is not None and delegate_variable_name != "":
        variables[delegate_variable_name] = delegate_value
    return variables


def set_variable(action_context: ActionContext, variable_name, variable_value):
    variables = action_context.unitContext.stageContext.pipelineContext.variables
    variables[variable_name] = variable_value
