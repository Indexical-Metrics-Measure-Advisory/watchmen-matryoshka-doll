import logging
import time

from storage.storage.engine_adaptor import MONGO
from storage.storage.exception.exception import InsertConflictError

from watchmen.common.utils.data_utils import get_id_name_by_datasource
from watchmen.config.config import settings
from watchmen.database.datasource.container import data_source_container
from watchmen.pipeline.core.action.utils import update_retry_callback, update_recovery_callback
from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import get_variables, ActionContext
from watchmen.pipeline.core.mapping.parse_mapping import parse_mappings
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.core.retry.retry_template import RetryPolicy, retry_template
from watchmen.pipeline.storage.read_topic_data import query_topic_data
from watchmen.pipeline.storage.write_topic_data import insert_topic_data, update_topic_data_one
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

log = logging.getLogger("app." + __name__)


def init(action_context: ActionContext):
    def merge_or_insert_topic():
        action = action_context.action
        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.topicId))
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
        status.type = "insert-or-merge-row"
        status.uid = action_context.get_pipeline_id()

        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData
        action = action_context.action
        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.topicId))

        pipeline_topic = action_context.get_pipeline_context().pipelineTopic
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

        status.value = mappings_results

        where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
        status.by = where_

        # todo
        # should not use find_one,use find_ and check the number of record
        target_data = query_topic_data(where_,
                                       target_topic, action_context.get_current_user())

        trigger_pipeline_data_list = []

        if target_data is None:
            try:
                if settings.STORAGE_ENGINE == MONGO:
                    mappings_results["version_"] = 0
                    mappings_results["aggregate_assist_"] = {}
                result = insert_topic_data(mappings_results,
                                           action_context.get_pipeline_id(),
                                           target_topic, action_context.get_current_user())
                trigger_pipeline_data_list.append(result)
                status.insertCount = status.insertCount + 1
                elapsed_time = time.time() - start
                status.completeTime = elapsed_time
                return status, trigger_pipeline_data_list
            except InsertConflictError as e:
                log.info("the insert failed because of conflict, try to update operator")

        args = [mappings_results, where_, target_topic, action_context.get_current_user()]
        retry_callback = (update_retry_callback, args)
        recovery_callback = (update_recovery_callback, args)
        execute_ = retry_template(retry_callback, recovery_callback, RetryPolicy())
        result = execute_()
        trigger_pipeline_data_list.append(result)
        status.updateCount = status.updateCount + 1
        elapsed_time = time.time() - start
        status.completeTime = elapsed_time
        return status, trigger_pipeline_data_list

    def not_aggregation_topic_merge_or_insert_topic():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "insert-or-merge-row"
        status.uid = action_context.get_pipeline_id()

        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData
        action = action_context.action
        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.topicId))

        pipeline_topic = action_context.get_pipeline_context().pipelineTopic
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

        status.value = mappings_results

        where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
        status.by = where_

        target_data = query_topic_data(where_,
                                       target_topic, action_context.get_current_user())

        trigger_pipeline_data_list = []

        if target_data is None:
            trigger_pipeline_data_list.append(
                insert_topic_data(mappings_results,
                                  action_context.get_pipeline_id(),
                                  target_topic, action_context.get_current_user()))
            status.insertCount = status.insertCount + 1

        else:

            trigger_pipeline_data_list.append(
                update_topic_data_one(mappings_results, target_data,
                                      action_context.get_pipeline_id(),
                                      target_data[get_id_name_by_datasource(
                                          data_source_container.get_data_source_by_id(target_topic.dataSourceId))],
                                      target_topic, action_context.get_current_user()))
            status.updateCount = status.updateCount + 1

        elapsed_time = time.time() - start
        status.completeTime = elapsed_time

        return status, trigger_pipeline_data_list

    return merge_or_insert_topic
