from pydantic import BaseModel

from watchmen.pipeline.model.trigger_type import TriggerType


class TriggerData(BaseModel):
    topicName:str =None
    triggerType:TriggerType=None
    data:dict =None
