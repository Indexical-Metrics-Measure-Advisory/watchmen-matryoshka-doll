from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.pipeline.core.dependency.graph.label import Label
from watchmen.pipeline.core.dependency.graph.node import Node
from watchmen.pipeline.core.dependency.graph.property import Property


def buildPipelineNode(pipeline):
    labels = buildPipelineLabels()
    property_dict = {"name": pipeline.name}
    properties = buildPipelineProperties(property_dict)
    pipeline_node = Node(**{
        'id': pipeline.pipelineId,
        'object_id': "pipeline",
        'name': pipeline.name,
        'labels': labels,
        'properties': properties
    })
    return pipeline_node


def buildPipelineProperties(properties: dict):
    property_list = []
    for key, value in properties.items():
        property_ = Property(**{
            'id': get_surrogate_key(),
            'name': key,
            'value': value
        })
        property_list.append(property_)
    return property_list


def buildPipelineLabels():
    labels = []
    label = Label(**{
        'id': get_surrogate_key(),
        'name': 'type',
        'value': 'pipeline'
    })
    labels.append(label)
    return labels
