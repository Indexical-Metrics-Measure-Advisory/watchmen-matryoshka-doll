from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.action.insert_or_merge_row import build_right_query, filter_condition
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


def init(action: UnitAction, pipeline_topic: Topic):
    def read_factor(raw_data, context):
        context_target_name = action.targetName
        topic = get_topic_by_id(action.topicId)
        factor = get_factor(action.factorId, topic)
        condition = action.by
        where_condition = build_right_query(condition, pipeline_topic, raw_data, topic)
        filter_where_condition = filter_condition(where_condition, 0)
        target_data = read_topic_data(filter_where_condition, topic.name, condition.mode)
        print("target_data :", target_data)
        print("factor.name  :", factor.name)
        if factor.name in target_data:
            context[context_target_name] = target_data[factor.name]
        print("context :", context)
        return context

    return read_factor
