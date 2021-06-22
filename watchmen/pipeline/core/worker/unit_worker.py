import logging

from watchmen.monitor.model.pipeline_monitor import UnitRunStatus
from watchmen.pipeline.core.context.action_context import ActionContext
from watchmen.pipeline.core.context.unit_context import UnitContext
from watchmen.pipeline.core.worker.action_worker import run_action
from watchmen.pipeline.single.stage.unit.mongo.index import __check_condition

log = logging.getLogger("app." + __name__)


def should_run(unitContext: UnitContext) -> bool:
    unit = unitContext.unit
    pipeline_topic = unitContext.stageContext.pipelineContext.pipelineTopic
    data = unitContext.stageContext.pipelineContext.data
    context = unitContext.stageContext.pipelineContext.variables
    return __check_condition(unit, pipeline_topic, data, context)


def run_unit(unitContext: UnitContext):
    loopVariableName = unitContext.unit.loopVariableName
    if loopVariableName is not None and loopVariableName != "":
        loopVariable = unitContext.stageContext.pipelineContext.variables[loopVariableName]
        #rint("loopVariable",loopVariable)
        if isinstance(loopVariable, list):
            for value in unitContext.stageContext.pipelineContext.variables[loopVariableName]:
                print("value", value)
                if unitContext.unit.do is not None:
                    print("should_run(unitContext)", should_run(unitContext))
                    if should_run(unitContext):
                        unitContext.unitStatus = UnitRunStatus()
                        # print("value", value)
                        for action in unitContext.unit.do:
                            actionContext = ActionContext(unitContext, action)
                            #print("actionContext", actionContext.action.type)
                            actionContext.delegateVariableName = loopVariableName
                            actionContext.delegateValue = value
                            run_action(actionContext)
                            unitContext.unitStatus.actions.append(actionContext.actionStatus)
        elif loopVariable is not None:  # the loop variable just have one element.
            if unitContext.unit.do is not None:
                if should_run(unitContext):
                    unitContext.unitStatus = UnitRunStatus()
                    for action in unitContext.unit.do:
                        actionContext = ActionContext(unitContext, action)
                        actionContext.delegateVariableName = loopVariableName
                        actionContext.delegateValue = loopVariable
                        run_action(actionContext)
                        unitContext.unitStatus.actions.append(actionContext.actionStatus)
    else:
        if unitContext.unit.do is not None:
            if should_run(unitContext):
                unitContext.unitStatus = UnitRunStatus()
                for action in unitContext.unit.do:
                    actionContext = ActionContext(unitContext, action)
                    run_action(actionContext)
                    unitContext.unitStatus.actions.append(actionContext.actionStatus)
