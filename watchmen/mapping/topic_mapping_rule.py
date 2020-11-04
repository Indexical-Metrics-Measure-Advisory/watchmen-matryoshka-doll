from pydantic import BaseModel
from typing import Dict

from watchmen.mapping.mapping_rule import MappingRule


class TopicMappingRule(BaseModel):
    topicMappingId: str = None
    targetTopicId: str = None
    lakeSchemaId: str = None
    factor_rules: Dict[ str, MappingRule] = {}








