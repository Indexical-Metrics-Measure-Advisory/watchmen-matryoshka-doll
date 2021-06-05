import datetime

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.pipeline.core.dependency.denpendence import Graph, add_edge, show_graph
from watchmen.pipeline.core.dependency.graph.property import Property
from watchmen.pipeline.core.dependency.graph.relationship import Relationship
from watchmen.pipeline.core.dependency.model.factor import buildFactorNode
from watchmen.pipeline.core.dependency.model.pipeline import buildPipelineNode
from watchmen.pipeline.core.dependency.model.topic import buildTopicNode
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_list
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

'''
def buildPipelineGraph(pipelines):
    already_see = []
    pipeline_graph = Graph(**{
        'nodes': [],
        'edges': 0,
        'adj': {}
    })
    for pipeline in pipelines:
        if pipeline.enabled:
            pipeline_node = buildPipelineNode(pipeline)
            pipeline_graph.nodes.append(pipeline_node)
            source_topic_node = buildTopicNode(get_topic_by_id(pipeline.topicId))
            pipeline_graph.nodes.append(source_topic_node)
            relationship_properties = buildRelationShipProperties({"type": "pipeline_and_topic"})
            relationship = buildRelationShip(source_topic_node, pipeline_node, relationship_properties)
            pipeline_graph = add_edge(pipeline_graph, relationship)
            for stage in pipeline.stages:
                for unit in stage.units:
                    for action in unit.do:
                        if action.type == 'insert-or-merge-row':
                            insert_or_update(action, already_see, pipeline_graph, pipeline_node)
                        elif action.type == 'copy-to-memory':
                            pass
                        elif action.type == 'insert-row':
                            insert_or_update(action, already_see, pipeline_graph, pipeline_node)
                        elif action.type == 'read-row':
                            if action.topicId in already_see:
                                pass
                            else:
                                topic = get_topic_by_id(action.topicId)
                                topic_node = buildTopicNode(topic)
                                pipeline_graph.nodes.append(topic_node)
                                already_see.append(topic_node.id)
                                relationship_properties = buildRelationShipProperties({"type": "topic_and_pipeline"})
                                relationship = buildRelationShip(topic_node, pipeline_node, relationship_properties)
                                pipeline_graph = add_edge(pipeline_graph, relationship)
                        elif action.type == 'merge-row':
                            insert_or_update(action, already_see, pipeline_graph, pipeline_node)
    show_graph(pipeline_graph)
'''


def pipelineExecutionPath(topic):
    format_ = ''
    graph = buildPipelinesGraph()
    for node in graph.nodes:
        if node.id == topic.topicId:
            printPipelineExecutionPath(node, graph, format_)


def printPipelineExecutionPath(node, graph, format_):
    print(format_ + node.name + '(' + node.object_id + ')' + '->')
    format_ = format_ + "    "
    for item in graph.adj.get(node.id, []):
        if len(graph.adj.get(item.id, [])) != 0:
            printPipelineExecutionPath(item, graph, format_)


def buildPipelinesGraph():
    already_see = []
    pipeline_graph = Graph(**{
        'nodes': [],
        'edges': 0,
        'adj': {}
    })
    pipelines = load_pipeline_list()
    start_tm = datetime.datetime.now()
    for pipeline in pipelines:
        if pipeline.enabled:
            buildPipelineGraph(pipeline, already_see, pipeline_graph)
    end_tm = datetime.datetime.now()
    print((end_tm - start_tm).seconds)
    show_graph(pipeline_graph)
    return pipeline_graph


def buildPipelineGraph(pipeline, already_see, pipeline_graph):
    pipeline_node = buildPipelineNode(pipeline)
    pipeline_graph.nodes.append(pipeline_node)
    if get_topic_by_id(pipeline.topicId) is None:
        return
    source_topic_node = buildTopicNode(get_topic_by_id(pipeline.topicId))
    if source_topic_node.id in already_see:
        pass
    else:
        pipeline_graph.nodes.append(source_topic_node)
        already_see.append(source_topic_node.id)
    relationship_properties = buildRelationShipProperties({"type": "topic_to_pipeline"})
    relationship = buildRelationShip(source_topic_node, pipeline_node, relationship_properties)
    pipeline_graph = add_edge(pipeline_graph, relationship)
    for stage in pipeline.stages:
        for unit in stage.units:
            for action in unit.do:
                if action.type == 'insert-or-merge-row':
                    insert_or_update(action, already_see, pipeline_graph, pipeline_node)
                elif action.type == 'copy-to-memory':
                    pass
                elif action.type == 'insert-row':
                    insert_or_update(action, already_see, pipeline_graph, pipeline_node)
                elif action.type == 'write-factor':
                    insert_or_update(action, already_see, pipeline_graph, pipeline_node)
                elif action.type == 'merge-row':
                    insert_or_update(action, already_see, pipeline_graph, pipeline_node)
                elif action.type == 'read-row':
                    read_(action, already_see, pipeline_graph, pipeline_node)
                elif action.type == 'read-rows':
                    read_(action, already_see, pipeline_graph, pipeline_node)
                elif action.type == 'read-factors':
                    read_(action, already_see, pipeline_graph, pipeline_node)
                elif action.type == 'read-factor':
                    read_(action, already_see, pipeline_graph, pipeline_node)
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


def insert_or_update(action, already_see, pipeline_graph, pipeline_node):
    topic = get_topic_by_id(action.topicId)
    topic_node = buildTopicNode(topic)
    if topic_node.id in already_see:
        pass
    else:
        pipeline_graph.nodes.append(topic_node)
        already_see.append(topic_node.id)
    relationship_properties = buildRelationShipProperties({"type": "pipeline_to_topic"})
    relationship = buildRelationShip(pipeline_node, topic_node, relationship_properties)
    pipeline_graph = add_edge(pipeline_graph, relationship)
    for map_ in action.mapping:
        factor = getFactorFromTopic(topic, map_.factorId)
        if factor is None:
            continue
        factor_node = buildFactorNode(factor)
        if factor_node.name == "changeId":
            pass
        else:
            if factor_node.id in already_see:
                pass
            else:
                pipeline_graph.nodes.append(factor_node)
                already_see.append(factor_node)
            relationship_properties = buildRelationShipProperties({"type": "pipeline_to_factor"})
            relationship = buildRelationShip(pipeline_node, factor_node, relationship_properties)
            pipeline_graph = add_edge(pipeline_graph, relationship)


def read_(action, already_see, pipeline_graph, pipeline_node):
    topic = get_topic_by_id(action.topicId)
    topic_node = buildTopicNode(topic)
    if topic_node.id in already_see:
        pass
    else:
        pipeline_graph.nodes.append(topic_node)
        already_see.append(topic_node.id)
    relationship_properties = buildRelationShipProperties({"type": "topic_to_pipeline"})
    relationship = buildRelationShip(topic_node, pipeline_node, relationship_properties)
    pipeline_graph = add_edge(pipeline_graph, relationship)
    if action.factorId is not None:
        factor = getFactorFromTopic(topic, action.factorId)
        factor_node = buildFactorNode(factor)
        if factor_node.id in already_see:
            pass
        else:
            pipeline_graph.nodes.append(factor_node)
            already_see.append(factor_node.id)
        relationship_properties = buildRelationShipProperties({"type": "factor_to_pipeline"})
        relationship = buildRelationShip(factor_node, pipeline_node, relationship_properties)
        add_edge(pipeline_graph, relationship)
