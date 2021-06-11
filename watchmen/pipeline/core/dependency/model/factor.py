from storage.snowflake.snowflake import get_surrogate_key
from watchmen.pipeline.core.dependency.graph.label import Label
from watchmen.pipeline.core.dependency.graph.node import Node
from watchmen.pipeline.core.dependency.graph.property import Property
from watchmen.topic.factor.factor import Factor


def buildFactorNode(factor: Factor):
    labels = buildFactorLabels()
    property_dict = {"name": factor.name}
    properties = buildFactorProperties(property_dict)
    factor_node = Node(**{
        'id': factor.factorId,
        'object_id': "factor",
        'name': factor.name,
        'labels': labels,
        'properties': properties
    })
    return factor_node


def buildFactorProperties(properties: dict):
    property_list = []
    for key, value in properties.items():
        property_ = Property(**{
            'id': get_surrogate_key(),
            'name': key,
            'value': value
        })
        property_list.append(property_)
    return property_list


def buildFactorLabels():
    labels = []
    label = Label(**{
        'id': get_surrogate_key(),
        'name': 'type',
        'value': 'factor'
    })
    labels.append(label)
    return labels
