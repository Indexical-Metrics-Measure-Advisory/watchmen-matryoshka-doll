from typing import List

import pandas as pd
from pydantic import BaseModel

from watchmen.space.subject.filter import Filter
from watchmen.space.subject.join import Join
from watchmen.space.subject.subject import Subject
from watchmen.topic.factor.factor import Factor
from watchmen.topic.storage.topic_data_storage import get_topic_instances
from watchmen.topic.topic import Topic


def merge_dataset(topics: [Topic], data_frames: dict, joins: [Join]) -> object:
    # create graph for joins
    join_graph = {}
    for topic in topics:
        graph_nodes = []
        for join in joins:
            if topic.name == join.left:
                graph_nodes.append(join.right)
            if topic.name == join.right:
                graph_nodes.append(join.left)
        join_graph[topic.name] = graph_nodes
    print(join_graph)
    # graph dfs to merge dataset
    dfs_searched = set()
    merged_dataset = None

    def graph_traversal_by_dfs(graph: dict, start: str, dataset: dict):
        nonlocal merged_dataset
        if start not in dfs_searched:
            if merged_dataset is None:
                merged_dataset = dataset[start]
            else:
                merged_dataset = merged_dataset.merge(dataset[start], on='@pk')
            dfs_searched.add(start)
        for node in graph[start]:
            if node not in dfs_searched:
                graph_traversal_by_dfs(graph, node, dataset)

    graph_traversal_by_dfs(join_graph, topics[0].name, data_frames)
    print(merged_dataset)
    del merged_dataset['_id_x']
    return merged_dataset


def get_report_dataset(topics: List[Topic], factors: List[Factor], joins: List[Join], filters: List[Filter]):
    topic_dataset = {}
    for topic in topics:
        docs = get_topic_instances(topic.name)
        topic_dataset[topic.name] = pd.DataFrame(list(docs)).set_index('@pk')
    data_master = merge_dataset(topics, topic_dataset, joins)
    query_str = ''
    for filter_condition in filters:
        if query_str == '':
            query_str = filter_condition.key + '== ' + '\'' + filter_condition.value + '\''
        else:
            query_str = query_str + '&' + filter_condition.key + '== ' + '\'' + filter_condition.value + '\''
    filter_data = data_master.query(query_str)
    columns = []
    for factor in factors:
        columns.append(factor.name)
    return filter_data[columns]


class Report(BaseModel):
    name: str
    subject: Subject

    def get_report_dataset(self):
        topics = getattr(self.subject, 'topics')
        factors = getattr(self.subject, 'factors')
        joins = getattr(self.subject, 'joins')
        filters = getattr(self.subject, 'filters')
        return get_report_dataset(topics, factors, joins, filters)
