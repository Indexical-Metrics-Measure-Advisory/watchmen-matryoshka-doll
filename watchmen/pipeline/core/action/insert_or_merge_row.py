import time

from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import get_variables
from watchmen.pipeline.core.mapping.parse_mapping import parse_mappings
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.single.stage.unit.mongo.index import run_mapping_rules, \
    build_query_conditions, __build_mongo_query, index_conditions
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import query_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import insert_topic_data, update_topic_data, \
    update_topic_data_one
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def init(actionContext):
    def merge_or_insert_topic():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "InsertAndMergeRow"
        status.uid = actionContext.unitContext.stageContext.pipelineContext.pipeline.pipelineId

        previous_data = actionContext.previousOfTriggerData
        current_data = actionContext.currentOfTriggerData
        action = actionContext.action
        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))

        pipeline_topic = actionContext.unitContext.stageContext.pipelineContext.pipelineTopic
        target_topic = get_topic_by_id(action.topicId)
        variables = get_variables(actionContext)

        # if there are aggregate functions, need lock the record to update
        mappings_results, having_aggregate_functions = parse_mappings(action.mapping,
                                                                      target_topic,
                                                                      previous_data,
                                                                      current_data,
                                                                      variables)
        status.mapping = mappings_results

        where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
        status.whereConditions = where_

        # todo
        target_data = query_topic_data(where_, target_topic.name) # should not use find_one,use find_ and check the number of record

        trigger_pipeline_data_list = []

        if target_data is None:
            trigger_pipeline_data_list.append(
                insert_topic_data(target_topic.name, mappings_results,
                                  actionContext.unitContext.stageContext.pipelineContext.pipeline.pipelineId))
            status.insertCount = status.insertCount + 1

        else:
            '''
            trigger_pipeline_data_list.append(
                update_topic_data(target_topic.name, mappings_results, target_data,
                                  actionContext.unitContext.stageContext.pipelineContext.pipeline.pipelineId, where_))
            '''
            trigger_pipeline_data_list.append(
                update_topic_data_one(target_topic.name, mappings_results, target_data,
                                      actionContext.unitContext.stageContext.pipelineContext.pipeline.pipelineId,
                                      target_data['id_']))
            status.updateCount = status.updateCount + 1

        elapsed_time = time.time() - start
        status.complete_time = elapsed_time

        # print("trigger_pipeline_data_list", trigger_pipeline_data_list)
        return variables, status, trigger_pipeline_data_list

    return merge_or_insert_topic
