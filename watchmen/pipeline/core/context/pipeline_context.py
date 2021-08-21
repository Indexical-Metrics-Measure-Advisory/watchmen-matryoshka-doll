from watchmen.auth.user import User
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.topic.topic import Topic


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

    def __init__(self, pipeline, data, current_user):
        self.pipeline = pipeline
        self.data = data
        self.currentUser = current_user
        self.previousOfTriggerData = data.get("old")
        self.currentOfTriggerData = data.get("new")
        self.variables = {}
