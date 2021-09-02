import logging
import time

from watchmen.common.utils.data_utils import get_id_name
from watchmen.config.config import settings
from watchmen.database.storage.engine_adaptor import MONGO
from watchmen.database.storage.exception.exception import InsertConflictError
from watchmen.database.storage.storage_template import topic_data_update_one_with_version, topic_data_update_one
from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import get_variables, ActionContext
from watchmen.pipeline.core.mapping.parse_mapping import parse_mappings
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.core.retry.retry_template import RetryPolicy, retry_template
from watchmen.pipeline.model.trigger_data import TriggerData
from watchmen.pipeline.storage.read_topic_data import query_topic_data
from watchmen.pipeline.storage.write_topic_data import insert_topic_data, update_topic_data_one
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

log = logging.getLogger("app." + __name__)


def update_recovery_callback(mappings_results, where_, target_topic):
    log.error("The maximum number of retry times (3) is exceeded, retry failed. Do recovery, "
              "mappings_results: {0}, where: {1}, target_topic: {2}".format(mappings_results, where_, target_topic))
    target_data = query_topic_data(where_,
                                   target_topic.name)
    if target_data is not None:
        id_ = target_data.get(get_id_name(), None)
        if id_ is not None:
            topic_data_update_one(id_, mappings_results, target_topic.name)
            data = {**target_data, **mappings_results}
            return TriggerData(topicName=target_topic.name,
                               triggerType="Update",
                               data={"new": data, "old": target_data})
        else:
            raise RuntimeError("when do update, the id_ {0} should not be None".format(id_))
    else:
        raise RuntimeError("target topic {0} recovery failed. where: {1}".format(target_topic, where_))


def update_retry_callback(mappings_results, where_, target_topic):
    target_data = query_topic_data(where_,
                                   target_topic.name)
    if target_data is not None:
        id_ = target_data.get(get_id_name(), None)
        version_ = target_data.get("version_", None)
        if id_ is not None and version_ is not None:
            mappings_results['version_'] = version_
            topic_data_update_one_with_version(id_, version_, mappings_results, target_topic.name)
            data = {**target_data, **mappings_results}
            return TriggerData(topicName=target_topic.name,
                               triggerType="Update",
                               data={"new": data, "old": target_data})
        else:
            raise RuntimeError("when do update, the id_ {0} and version_ {1} should not be None".format(id_, version_))
    else:
        raise RuntimeError("insert or merge action failed")


def init(action_context: ActionContext):
    def merge_or_insert_topic():
        action = action_context.action
        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))
        target_topic = get_topic_by_id(action.topicId)
        if target_topic.type == "aggregate":
            return aggregation_topic_merge_or_insert_topic()
        else:
            return not_aggregation_topic_merge_or_insert_topic()

    def aggregation_topic_merge_or_insert_topic():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "InsertAndMergeRow"
        status.uid = action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId

        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData
        action = action_context.action
        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))

        pipeline_topic = action_context.unitContext.stageContext.pipelineContext.pipelineTopic
        target_topic = get_topic_by_id(action.topicId)
        variables = get_variables(action_context)

        # todo
        # if there are aggregate functions, need lock the record to update
        # consider use the flag of "having_aggregate_functions" for the distributed lock in the future
        mappings_results, having_aggregate_functions = parse_mappings(action.mapping,
                                                                      target_topic,
                                                                      previous_data,
                                                                      current_data,
                                                                      variables)

        status.mapping = mappings_results

        where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
        status.whereConditions = where_

        # todo
        # should not use find_one,use find_ and check the number of record
        target_data = query_topic_data(where_,
                                       target_topic.name)

        trigger_pipeline_data_list = []

        if target_data is None:
            try:
                if settings.STORAGE_ENGINE == MONGO:
                    mappings_results["version_"] = 0
                    mappings_results["aggregate_assist_"] = {}
                result = insert_topic_data(target_topic.name, mappings_results,
                                           action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId)
                trigger_pipeline_data_list.append(result)
                status.insertCount = status.insertCount + 1
                elapsed_time = time.time() - start
                status.complete_time = elapsed_time
                return status, trigger_pipeline_data_list
            except InsertConflictError as e:
                log.info("the insert failed because of conflict, try to update operator")

        args = [mappings_results, where_, target_topic]
        retry_callback = (update_retry_callback, args)
        recovery_callback = (update_recovery_callback, args)
        execute_ = retry_template(retry_callback, recovery_callback, RetryPolicy())
        execute_()

        status.updateCount = status.updateCount + 1
        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, trigger_pipeline_data_list

    def not_aggregation_topic_merge_or_insert_topic():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "InsertAndMergeRow"
        status.uid = action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId

        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData
        action = action_context.action
        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))

        pipeline_topic = action_context.unitContext.stageContext.pipelineContext.pipelineTopic
        target_topic = get_topic_by_id(action.topicId)

        variables = get_variables(action_context)

        # todo
        # if there are aggregate functions, need lock the record to update
        # consider use the flag of "having_aggregate_functions" for the distributed lock in the future
        mappings_results, having_aggregate_functions = parse_mappings(action.mapping,
                                                                      target_topic,
                                                                      previous_data,
                                                                      current_data,
                                                                      variables)

        status.mapping = mappings_results

        where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
        status.whereConditions = where_

        # todo
        # should not use find_one,use find_ and check the number of record
        target_data = query_topic_data(where_,
                                       target_topic.name)

        trigger_pipeline_data_list = []

        if target_data is None:
            trigger_pipeline_data_list.append(
                insert_topic_data(target_topic.name, mappings_results,
                                  action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId))
            status.insertCount = status.insertCount + 1

        else:
            trigger_pipeline_data_list.append(
                update_topic_data_one(target_topic.name, mappings_results, target_data,
                                      action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId,
                                      target_data[get_id_name()]))
            status.updateCount = status.updateCount + 1

        elapsed_time = time.time() - start
        status.complete_time = elapsed_time

        return status, trigger_pipeline_data_list

    return merge_or_insert_topic
