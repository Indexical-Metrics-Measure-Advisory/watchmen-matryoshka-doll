import time

from watchmen.common.constants import pipeline_constants
from watchmen.monitor.model.pipeline_monitor import UnitStatus
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import run_mapping_rules, \
    build_query_conditions, __build_mongo_query
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import query_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import insert_topic_data, update_topic_data
from watchmen.pipeline.single.stage.unit.utils import PIPELINE_UID
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


def init(action: UnitAction, pipeline_topic: Topic):
    def merge_or_insert_topic(instance, context):
        raw_data, old_value = instance[pipeline_constants.NEW], instance[pipeline_constants.OLD]
        unit_action_status = UnitStatus(type=action.type)
        start = time.time()
        pipeline_uid = context[PIPELINE_UID]
        unit_action_status.uid = pipeline_uid

        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))

        target_topic = get_topic_by_id(action.topicId)
        mapping_results, mapping_logs = run_mapping_rules(action.mapping, target_topic, raw_data, pipeline_topic)
        joint_type, where_condition = build_query_conditions(action.by, pipeline_topic, raw_data, target_topic, context)
        for index in range(len(mapping_results)):
            mongo_query = __build_mongo_query(joint_type, where_condition)
            target_data = query_topic_data(mongo_query, target_topic.name)
            if target_data is None:
                insert_topic_data(target_topic.name, mapping_results[index], pipeline_uid)
                unit_action_status.insertCount = unit_action_status.insertCount + 1
            else:
                update_topic_data(target_topic.name, mapping_results[index], target_data, pipeline_uid)
                unit_action_status.updateCount = unit_action_status.updateCount + 1

        unit_action_status.mapping = mapping_logs
        elapsed_time = time.time() - start
        unit_action_status.complete_time = elapsed_time
        return context, unit_action_status

    return merge_or_insert_topic
