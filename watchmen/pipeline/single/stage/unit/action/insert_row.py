import logging
from datetime import datetime

from watchmen.monitor.model.pipeline_monitor import UnitStatus
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import run_mapping_rules, find_pipeline_topic_condition, \
    filter_condition
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import insert_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_execute_time
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


def init(action: UnitAction, pipeline_topic: Topic):
    def insert_topic(raw_data, context):
        unit_action_status = UnitStatus()
        unit_action_status.type = action.type
        start_time = datetime.now()

        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))

        target_topic = get_topic_by_id(action.topicId)

        mapping_results = run_mapping_rules(action.mapping, target_topic, raw_data, pipeline_topic)

        conditions = action.by

        where_condition = find_pipeline_topic_condition(conditions, pipeline_topic, raw_data, target_topic)

        for index in range(len(mapping_results)):
            filter_where_condition = filter_condition(where_condition, index)

            target_data = read_topic_data(filter_where_condition, target_topic.name, conditions.jointType)
            if target_data is None:
                insert_topic_data(target_topic.name, mapping_results[index])
            else:
                raise Exception("target_topic row already exist")

        unit_action_status.complete_time = get_execute_time(start_time)
        return context, unit_action_status

    return insert_topic
