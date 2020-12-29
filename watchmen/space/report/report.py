from pydantic import BaseModel

from watchmen.topic.storage import get_topic_instances
from watchmen.topic.topic import Topic
from watchmen.space.factor.factor import Factor
from watchmen.space.subject.filter import Filter
from watchmen.space.subject.join import Join
from watchmen.space.subject.subject import Subject
import pandas as pd


def merge_dataset(topics: [Topic], dataframes: dict, joins: [Join]) -> object:
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

    def graph_traversal_by_dfs(graph: dict, start: str, datasets: dict):
        nonlocal merged_dataset
        if start not in dfs_searched:
            if merged_dataset is None:
                merged_dataset = datasets[start]
            else:
                merged_dataset = merged_dataset.merge(datasets[start], on='@pk')
            dfs_searched.add(start)
        for node in graph[start]:
            if node not in dfs_searched:
                graph_traversal_by_dfs(graph, node, datasets)

    graph_traversal_by_dfs(join_graph, topics[0].name, dataframes)
    print(merged_dataset)
    del merged_dataset['_id_x']
    return merged_dataset


def get_report_dataset(topics: [Topic], factors: [Factor], joins: [Join], filters: [Filter]):
    topic_datasets = {}
    for topic in topics:
        docs = get_topic_instances(topic.name)
        topic_datasets[topic.name] = pd.DataFrame(list(docs)).set_index('@pk')
    data_master = merge_dataset(topics, topic_datasets, joins)
    query_str = ''
    for filter in filters:
        if query_str == '':
            query_str = filter.key + '== ' + '\'' + filter.value + '\''
        else:
            query_str = query_str + '&' + filter.key + '== ' + '\'' + filter.value + '\''
    filter_data = data_master.query(query_str)
    columns = []
    for factor in factors:
        columns.append(factor.name)
    print(filter_data[columns])
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
