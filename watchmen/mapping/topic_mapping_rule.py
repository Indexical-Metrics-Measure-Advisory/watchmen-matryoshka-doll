from pydantic import BaseModel
from typing import Dict

from watchmen.mapping.mapping_rule import MappingRule


class TopicMappingRule(BaseModel):
    topicMappingId: str = None
    sourceTopicId: str = None
    sourceTopicName: str = None
    targetTopicId: str = None
    targetTopicName: str = None
    factor_rules: Dict[ str, MappingRule] = {}








