from watchmen.pipeline.model.pipeline import UnitAction, CompositeCondition
from watchmen.pipeline.single.stage.unit.action.merge_row import check_condition
from watchmen.pipeline.single.stage.unit.utils.units_func import get_value
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


def find_merge_data(condition: CompositeCondition,target_topic,pipeline_topic,raw_data):
    mode = condition.mode
    target_topic_data = {}

    for sub_condition in condition.children:
        left_value = get_value(sub_condition.left,target_topic_data,target_topic)
        operator = sub_condition.operator
        right_value = get_value(sub_condition.right,raw_data,pipeline_topic)
        if mode == "and":
            result = False
            if check_condition(operator, left_value, right_value):
                result = True
            return result
        elif mode == "or":
            if check_condition(operator, left_value, right_value):
                return True

    # read data factor

    # read row in target topic data
    # return match row
    return {}


def init(action: UnitAction, pipeline_topic: Topic):
    def merge_topic(raw_data):
        print("action:", action)
        if action.topicId is not None:
            target_topic = get_topic_by_id(action.topicId)
            condition = action.by
            data = find_merge_data(condition,target_topic,pipeline_topic,raw_data)
            mapping_list = action.mapping
            if data is None:
                pass  # insert
            else:
                pass  # update

        # TODO save data

    return merge_topic
