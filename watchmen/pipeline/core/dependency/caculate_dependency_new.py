import datetime

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.pipeline.core.dependency.denpendence_new import Graph, add_edge
from watchmen.pipeline.core.dependency.graph.property import Property
from watchmen.pipeline.core.dependency.graph.relationship import Relationship
from watchmen.pipeline.core.dependency.model.factor import buildFactorNode
from watchmen.pipeline.core.dependency.model.pipeline import buildPipelineNode
from watchmen.pipeline.core.dependency.model.topic import buildTopicNode
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_list
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def pipelineExecutionPath(topic):
    result = []
    format_ = ''
    graph = buildPipelinesGraph()
    printPipelineExecutionPath(graph.nodes[topic.topicId], graph, format_, result)
    return result


def printPipelineExecutionPath(node, graph, format_, result):
    if len(graph.adj.get(node.id, {})) != 0:
        # print(format_ + node.name + '(' + node.object_id + ')' + '->')
        result.append(format_ + node.name + '(' + node.object_id + ')' + '->')
    format_ = format_ + "    "
    for key, value in graph.adj.get(node.id, {}).items():
        printPipelineExecutionPath(value, graph, format_, result)


def buildPipelinesGraph():
    pipeline_graph = Graph(**{
        'nodes': {},
        'edges': 0,
        'adj': {}
    })
    pipelines = load_pipeline_list()
    start_tm = datetime.datetime.now()
    for pipeline in pipelines:
        if pipeline.enabled:
            buildPipelineGraph(pipeline, pipeline_graph)
    end_tm = datetime.datetime.now()
    #print((end_tm - start_tm).seconds)
    # show_graph(pipeline_graph)
    return pipeline_graph


def buildPipelineGraph(pipeline, pipeline_graph):
    pipeline_node = buildPipelineNode(pipeline)
    pipeline_graph.nodes[pipeline_node.id] = pipeline_node
    source_topic = get_topic_by_id(pipeline.topicId)
    if source_topic is None:
        return
    source_topic_node = buildTopicNode(source_topic)
    pipeline_graph.nodes[source_topic_node.id] = source_topic_node
    relationship_properties = buildRelationShipProperties({"type": "topic_to_pipeline"})
    relationship = buildRelationShip(source_topic_node, pipeline_node, relationship_properties)
    pipeline_graph = add_edge(pipeline_graph, relationship)
    for stage in pipeline.stages:
        for unit in stage.units:
            for action in unit.do:
                if action.type == 'insert-or-merge-row':
                    insert_or_update(action, pipeline_graph, pipeline_node)
                elif action.type == 'copy-to-memory':
                    pass
                elif action.type == 'insert-row':
                    insert_or_update(action, pipeline_graph, pipeline_node)
                elif action.type == 'write-factor':
                    insert_or_update(action, pipeline_graph, pipeline_node)
                elif action.type == 'merge-row':
                    insert_or_update(action, pipeline_graph, pipeline_node)
                elif action.type == 'read-row':
                    read_(action, pipeline_graph, pipeline_node)
                elif action.type == 'read-rows':
                    read_(action, pipeline_graph, pipeline_node)
                elif action.type == 'read-factors':
                    read_(action, pipeline_graph, pipeline_node)
                elif action.type == 'read-factor':
                    read_(action, pipeline_graph, pipeline_node)
                elif action.type == 'exists':
                    pass
                elif action.type == 'alarm':
                    pass
                else:
                    raise ("action not support:" + action.type)


def buildRelationShip(left, right, properties):
    relationship = Relationship(**{
        'id': get_surrogate_key(),
        'name': 'link',
        'direction': 'one-way',
        'properties': properties,
        'left': left,
        'right': right
    })
    return relationship


def buildRelationShipProperties(properties: dict):
    property_list = []
    for key, value in properties.items():
        property_ = Property(**{
            'id': get_surrogate_key(),
            'name': key,
            'value': value
        })
        property_list.append(property_)
    return property_list


def getFactorFromTopic(topic, factorId):
    for factor in topic.factors:
        if factor.factorId == factorId:
            return factor


def insert_or_update(action, pipeline_graph, pipeline_node):
    topic_node = pipeline_graph.nodes.get(action.topicId)
    if topic_node is None:
        topic = get_topic_by_id(action.topicId)
        topic_node = buildTopicNode(topic)
        pipeline_graph.nodes[topic_node.id] = topic_node
    relationship_properties = buildRelationShipProperties({"type": "pipeline_to_topic"})
    relationship = buildRelationShip(pipeline_node, topic_node, relationship_properties)
    pipeline_graph = add_edge(pipeline_graph, relationship)
    for map_ in action.mapping:
        factor = getFactorFromTopic(topic_node.object_, map_.factorId)
        if factor is None:
            continue
        factor_node = buildFactorNode(factor)
        if factor_node.name == "changeId":
            pass
        else:
            pipeline_graph.nodes[factor_node.id] = factor_node
            relationship_properties = buildRelationShipProperties({"type": "pipeline_to_factor"})
            relationship = buildRelationShip(pipeline_node, factor_node, relationship_properties)
            pipeline_graph = add_edge(pipeline_graph, relationship)


def read_(action, pipeline_graph, pipeline_node):
    topic_node = pipeline_graph.nodes.get(action.topicId)
    if topic_node is None:
        topic = get_topic_by_id(action.topicId)
        topic_node = buildTopicNode(topic)
        pipeline_graph.nodes[topic_node.id] = topic_node
    relationship_properties = buildRelationShipProperties({"type": "topic_to_pipeline"})
    relationship = buildRelationShip(topic_node, pipeline_node, relationship_properties)
    pipeline_graph = add_edge(pipeline_graph, relationship)
    if action.factorId is not None:
        factor = getFactorFromTopic(topic_node.object_, action.factorId)
        factor_node = buildFactorNode(factor)
        pipeline_graph.nodes[factor_node.id] = factor_node
        relationship_properties = buildRelationShipProperties({"type": "factor_to_pipeline"})
        relationship = buildRelationShip(factor_node, pipeline_node, relationship_properties)
        add_edge(pipeline_graph, relationship)
