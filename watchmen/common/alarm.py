from pydantic.main import BaseModel


class AlarmMessage(BaseModel):
    severity: str = None
    message: str = None
    pipelineId: str = None
    topicId: str = None