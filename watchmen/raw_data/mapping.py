from model.model.common.watchmen_model import WatchmenModel


class Mapping(WatchmenModel):
    mapping_id: int
    source_entity_id: int
    source_entity_name: str
    target_topic_id: int
    target_topic_name: str
    mapping_detail_list: list
