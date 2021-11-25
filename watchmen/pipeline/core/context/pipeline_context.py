from model.model.common.user import User
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus
from model.model.pipeline.pipeline import Pipeline
from model.model.topic.topic import Topic


class PipelineContext:
    pipeline: Pipeline
    data: dict
    previousOfTriggerData: dict
    currentOfTriggerData: dict
    variables: dict
    topics: list
    instanceId: str
    pipelineTopic: Topic
    pipelineStatus: PipelineRunStatus
    pipeline_trigger_merge_list = []
    currentUser: User = None
    traceId: str = None

    def __init__(self, pipeline, data, current_user, trace_id):
        self.traceId = trace_id
        self.pipeline = pipeline
        self.data = data
        self.currentUser = current_user
        self.previousOfTriggerData = data.get("old")
        self.currentOfTriggerData = data.get("new")
        self.variables = {}
