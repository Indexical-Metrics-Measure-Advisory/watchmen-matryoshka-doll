# import json
import logging
import time

from watchmen.common.constants import pipeline_constants
from watchmen.monitor.model.pipeline_monitor import InsertAction
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import run_mapping_rules
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import insert_topic_data
from watchmen.pipeline.single.stage.unit.utils import PIPELINE_UID
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


def init(action: UnitAction, pipeline_topic: Topic):
    def insert_topic(instance, context):
        raw_data, old_value = instance[pipeline_constants.NEW], instance[pipeline_constants.OLD]
        unit_action_status = InsertAction(type=action.type)
        start = time.time()
        pipeline_uid = context[PIPELINE_UID]
        unit_action_status.uid = pipeline_uid
        # print(json.loads(raw_data))
        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))

        target_topic = get_topic_by_id(action.topicId)
        log.info("run target_topic {0}".format(target_topic.name))
        mapping_results = run_mapping_rules(action.mapping, target_topic, raw_data, pipeline_topic, context)
        log.info("mapping_results:{0}".format(mapping_results))
        unit_action_status.mapping = mapping_results
        trigger_pipeline_data_list = []
        for index, item in enumerate(mapping_results):
            trigger_pipeline_data_list.append(insert_topic_data(target_topic.name, item, pipeline_uid))
            unit_action_status.insertCount = unit_action_status.insertCount + 1

        elapsed_time = time.time() - start
        unit_action_status.complete_time = elapsed_time
        return context, unit_action_status, trigger_pipeline_data_list

    return insert_topic
