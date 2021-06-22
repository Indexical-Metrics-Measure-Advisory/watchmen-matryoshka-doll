from queue import SimpleQueue
from typing import Dict
from typing import List

from pydantic import BaseModel

from watchmen.pipeline.core.dependency.graph.node import Node
from watchmen.pipeline.core.dependency.graph.relationship import Relationship


class Graph(BaseModel):
    nodes: List[Node] = None
    edges: int = 0
    adj: Dict[str, List[Node]] = {}
    relationships: List[Relationship] = []


def add_edge(graph: Graph, relationship: Relationship) -> Graph:
    if len(graph.adj.get(relationship.left.id, [])) == 0:
        graph.adj[relationship.left.id] = [relationship.right]
        graph.relationships.append(relationship)
    else:
        count = 0
        for node in graph.adj.get(relationship.left.id):
            if node.id == relationship.right.id:
                count = count + 1
        if count == 0:
            graph.adj.get(relationship.left.id).append(relationship.right)
            graph.relationships.append(relationship)
    '''
    if len(graph.adj.get(relationship.right.id, [])) == 0:
        graph.adj[relationship.right.id] = [relationship.left]
    else:
        graph.adj.get(relationship.right.id).append(relationship.left)
    '''
    graph.edges = graph.edges + 1
    return graph


def show_graph(graph: Graph):
    for node in graph.nodes:
        if len(graph.adj.get(node.id, [])) != 0:
            #print(node.name + '(' + node.object_id + ')' + '->')
            for item in graph.adj.get(node.id, []):
                pass



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
