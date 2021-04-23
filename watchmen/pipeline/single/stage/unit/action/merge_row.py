import logging
import time

from watchmen.common.constants import pipeline_constants
from watchmen.monitor.model.pipeline_monitor import UnitActionStatus
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import run_mapping_rules, build_query_conditions, \
    __build_mongo_query, index_conditions
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import query_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import update_topic_data
from watchmen.pipeline.single.stage.unit.utils import PIPELINE_UID
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


def init(action: UnitAction, pipeline_topic: Topic):
    def merge_topic(instance, context):
        raw_data, old_value = instance[pipeline_constants.NEW], instance[pipeline_constants.OLD]
        unit_action_status = UnitActionStatus(type=action.type)
        start = time.time()
        pipeline_uid = context[PIPELINE_UID]
        unit_action_status.uid = pipeline_uid

        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))

        target_topic = get_topic_by_id(action.topicId)
        mapping_results = run_mapping_rules(action.mapping, target_topic, raw_data, pipeline_topic, context)
        joint_type, where_condition = build_query_conditions(action.by, pipeline_topic, raw_data, target_topic, context)
        unit_action_status.whereConditions = where_condition
        unit_action_status.mapping = mapping_results
        trigger_pipeline_data_list = []
        for index, mapping_result in enumerate(mapping_results):
            mongo_query = __build_mongo_query(joint_type, index_conditions(where_condition, index))
            target_data = query_topic_data(mongo_query, target_topic.name)
            if target_data is None:
                raise Exception("can't insert data in merge row action ")
            else:
                trigger_pipeline_data_list.append(
                    update_topic_data(target_topic.name, mapping_result, target_data, pipeline_uid))
                unit_action_status.updateCount = unit_action_status.updateCount + 1

        elapsed_time = time.time() - start
        unit_action_status.complete_time = elapsed_time
        return context, unit_action_status, trigger_pipeline_data_list

    return merge_topic
