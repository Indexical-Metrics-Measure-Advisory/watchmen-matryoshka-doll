from pydantic import BaseModel

from watchmen.space.factor.factor import Factor
from watchmen.raw_data.data_entity import Attribute


class Mapping(BaseModel):
    mapping_id: int
    source_entity_id: int
    source_entity_name: str
    target_topic_id: int
    target_topic_name: str
    mapping_detail_list: list


class MappingDetail(BaseModel):
    source_attr: Attribute
    target_factor: Factor
