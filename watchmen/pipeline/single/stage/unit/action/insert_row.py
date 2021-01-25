import logging

from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import run_mapping_rules
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


def init(action: UnitAction, pipeline_topic: Topic):
    def insert_topic(raw_data):
        log.info("action: {0}".format(action))
        if action.topicId is not None:
            target_topic = get_topic_by_id(action.topicId)
            # condition = action.by
            # data = get_target_data(condition, target_topic, pipeline_topic, raw_data)
            mapping_list = action.mapping
            mapping_result = run_mapping_rules(mapping_list, target_topic, raw_data, pipeline_topic)
            # if data is None:
            # insert_topic_data(target_topic.name, mapping_result)

    return insert_topic
