from typing import Dict
from typing import List

from pydantic import BaseModel

from watchmen.pipeline.core.dependency.graph.node import Node
from watchmen.pipeline.core.dependency.graph.relationship import Relationship


class Graph(BaseModel):
    nodes: Dict[str, Node] = {}
    edges: int = 0
    adj: Dict[str, Dict[str, Node]] = {}
    relationships: List[Relationship] = []


def add_edge(graph: Graph, relationship: Relationship) -> Graph:
    if len(graph.adj.get(relationship.left.id, {})) == 0:
        graph.adj[relationship.left.id] = {relationship.right.id: relationship.right}
        graph.relationships.append(relationship)
    else:
        graph.adj.get(relationship.left.id)[relationship.right.id] = relationship.right
        graph.relationships.append(relationship)
    graph.edges = graph.edges + 1
    return graph


def show_graph(graph: Graph):
    for key, node in graph.nodes.items():
        if len(graph.adj.get(node.id, {})) != 0:
            print(node.name + '(' + node.object_id + ')' + '->')
            for k, item in graph.adj.get(node.id, {}).items():
                print(item.name + '(' + item.object_id + ')')
            print('\n')
    print(graph.edges)


'''
def bfs(node: Node, graph: Graph):
    queue = SimpleQueue()
    marked: dict = {node.id: True}
    queue.put(node)
    while queue.qsize() > 0:
        item = queue.get()
        if graph.adj[item.id] is not None:
            print("visited vertex: " + item.name)
        for v in graph.adj[item.id]:
            if not marked.get(v.id, False):
                marked[v.id] = True
                queue.put(v)
'''
