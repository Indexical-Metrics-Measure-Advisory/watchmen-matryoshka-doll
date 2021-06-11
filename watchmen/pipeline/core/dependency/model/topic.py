from storage.snowflake.snowflake import get_surrogate_key
from watchmen.pipeline.core.dependency.graph.label import Label
from watchmen.pipeline.core.dependency.graph.node import Node
from watchmen.pipeline.core.dependency.graph.property import Property
from watchmen.topic.topic import Topic


def buildTopicNode(topic: Topic):
    labels = buildTopicLabels(topic)
    property_dict = {"name": topic.name}
    properties = buildTopicProperties(property_dict)
    topic_node = Node(**{
        'id': topic.topicId,
        'object_id': "topic",
        'object_': topic,
        'name': topic.name,
        'labels': labels,
        'properties': properties
    })
    return topic_node


def buildTopicProperties(properties):
    property_list = []
    for key, value in properties.items():
        property_ = Property(**{
            'id': get_surrogate_key(),
            'name': key,
            'value': value
        })
        property_list.append(property_)
    return property_list


def buildTopicLabels(topic):
    labels = []
    label = Label(**{
        'id': get_surrogate_key(),
        'name': 'type',
        'value': 'topic'
    })
    labels.append(label)
    return labels
