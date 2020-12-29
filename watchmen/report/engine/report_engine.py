import pandas as pd
from watchmen.topic.storage import get_topic_instances


class Topic:
    id: int = None
    name: str = ''
    type: str = ''


class Factor:
    id: int = None
    name: str = ''
    type: str = ""
    topic: Topic = None


class Filter:
    factor: Factor = None
    operator: str = ''
    value: str = ''


class Join:
    left: str = ''
    right: str = ''
    key: str = ''


class Subject:
    factors: [Factor] = None
    filters: [Filter] = None
    joins: [Join] = None


def report(subject: Subject):
    pass


def report(topics: [Topic], joins: [Join], filters, factors):
    dataframes = {}
    for topic in topics:
        docs = get_topic_instances(topic.name)
        dataframes[topic.name] = pd.DataFrame(list(docs)).set_index('@pk')
    data_master = join_dataframe(topics, dataframes, joins)

    query_str = ''
    for filter in filters:
        if query_str == '':
            query_str = filter.name + '== ' + '\''+ filter.value +'\''
        else:
            query_str = query_str + '&' + filter.name + '== ' + '\''+ filter.value + '\''
    filter_data = data_master.query(query_str)
    columns = []
    for factor in factors:
        columns.append(factor.name)
    print(filter_data[columns])



def join_dataframe(topics, dataframes, joins):
    graph = {}
    for topic in topics:
        nodes = []
        for join in joins:
            if topic.name == join.left:
                nodes.append(join.right)
            if topic.name == join.right:
                nodes.append(join.left)
        graph[topic.name] = nodes
    print(graph)
    dfs(graph, topics[0].name, dataframes)
    print(DFS_TEMP)
    del DFS_TEMP['_id_x']
    return DFS_TEMP


DFS_SEARCHED = set()

DFS_TEMP = None


def dfs(graph, start, dataframes):
    global DFS_TEMP
    if start not in DFS_SEARCHED:
        if DFS_TEMP is None:
            DFS_TEMP = dataframes[start]
        else:
            DFS_TEMP = DFS_TEMP.merge(dataframes[start], on='@pk')
        DFS_SEARCHED.add(start)
    for node in graph[start]:
        if node not in DFS_SEARCHED:
            dfs(graph, node, dataframes)


# construct topics
topics: [Topic] = []
policy_topic = Topic()
policy_topic.__setattr__('name', 'test_report_policy_data_col')
topics.append(policy_topic)
customer_topic = Topic()
customer_topic.__setattr__('name', 'test_report_customer_data_col')
topics.append(customer_topic)

factors: [Factor] = []
factor1 = Factor()
factor1.__setattr__('name', 'policyCode')
factor1.__setattr__('topic', policy_topic)
factors.append(factor1)
factor2 = Factor()
factor2.__setattr__('name', 'accoName')
factor2.__setattr__('topic', customer_topic)
factors.append(factor2)
factor3 = Factor()
factor3.__setattr__('name', 'telephone')
factor3.__setattr__('topic', customer_topic)
factors.append(factor3)
factor4 = Factor()
factor4.__setattr__('name', 'birthDate')
factor4.__setattr__('topic', customer_topic)
factors.append(factor4)

joins = []
join1 = Join()
join1.__setattr__('left', 'test_report_policy_data_col')
join1.__setattr__('right', 'test_report_customer_data_col')
join1.__setattr__('key', '@pk')
joins.append(join1)

filters= []
filter1 = Filter()
filter1.__setattr__('name', 'address1')
filter1.__setattr__('value', '北海道')
filters.append(filter1)
filter2 = Filter()
filter2.__setattr__('name', 'birthDate')
filter2.__setattr__('value', '2010-10-10')
filters.append(filter2)

report(topics, joins, filters, factors)

# join_dataframe(topics,joins)
'''
def generate_query(topics: [Topic], factors: [Factor], filters, groups):

    lookup_stage = {'$lookup': {}}
    lookup_parameters = {'from': '', 'localField': '', 'foreignField': '', 'as': ''}
    unwind_stage = {'$unwind': ''}
    match_stage = {'$match': {}}
    groups_stage = {'$group': {}}
    project_stage = {'$project': {}}

    # operator logical
    operator_or = {'$or': []}
    operator_and = {'$and': []}

    # operator_comparison
    operator_eq = {'$eq': ''}


    if len(topics) > 1:
        stage = {}
        pipeline = []
        #papers.aggregate(pipeline)
    else:
        topic_name = topics[0].name
        topic_data_col = db.get_collection(topic_name)
        topic_data_col.find({})
'''

'''
GRAPH = {
    'A': ['B', 'F'],
    'B': ['C', 'I', 'G'],
    'C': ['B', 'I', 'D'],
    'D': ['C', 'I', 'G', 'H', 'E'],
    'E': ['D', 'H', 'F'],
    'F': ['A', 'G', 'E'],
    'G': ['B', 'F', 'H', 'D'],
    'H': ['G', 'D', 'E'],
    'I': ['B', 'C', 'D'],
}

DFS_SEARCHED = set()


def dfs(graph, start):
    if start not in DFS_SEARCHED:
        print(start)
        DFS_SEARCHED.add(start)
    for node in graph[start]:
        if node not in DFS_SEARCHED:
            dfs(graph, node)


print('dfs:')
dfs(GRAPH, 'A')  # A B C I D G F E H
'''
