from watchmen.topic.storage import save_topic_instances
from watchmen.topic.topic import Topic
from watchmen.space.factor.factor import Factor
from watchmen.space.subject.join import Join
from watchmen.space.subject.filter import Filter
from watchmen.space.subject.subject import Subject
from watchmen.space.report.report import Report

import json


def import_report_data():
    # Reading the json as a dict, policy information
    with open('../assert/data/report_test_policy.json') as json_data:
        policy_data = json.load(json_data, encoding='utf-8')

    # import policy data in master topic
    save_topic_instances('test_report_policy_data_col', policy_data)

    # Reading the json as a dict, customer information
    with open('../assert/data/report_test_customer.json') as json_data:
        customer_data = json.load(json_data, encoding='utf-8')

    # import customer data in master topic
    save_topic_instances('test_report_customer_data_col', customer_data)


def get_report_dataset():
    # construct topics
    topics: [Topic] = []
    policy_topic = Topic(**{'topic_id': 1, 'name': 'test_report_policy_data_col', 'topic_type': 'policy'})
    customer_topic = Topic(**{'topic_id': 2, 'name': 'test_report_customer_data_col', 'topic_type': 'customer'})
    topics.append(policy_topic)
    topics.append(customer_topic)

    factors: [Factor] = []
    factor1 = Factor(**{'id': 1, 'name': 'policyCode', 'type': 'str', 'topic': policy_topic})
    factor2 = Factor(**{'id': 2, 'name': 'accoName', 'type': 'str', 'topic': customer_topic})
    factor3 = Factor(**{'id': 3, 'name': 'telephone', 'type': 'int', 'topic': customer_topic})
    factor4 = Factor(**{'id': 4, 'name': 'birthDate', 'type': 'date', 'topic': customer_topic})
    factors.append(factor1)
    factors.append(factor2)
    factors.append(factor3)
    factors.append(factor4)

    joins = []
    join1 = Join(
        **{'id': 1, 'left': 'test_report_policy_data_col', 'right': 'test_report_customer_data_col', 'key': '@pk'})
    joins.append(join1)

    filters = []
    filter1 = Filter(**{'id': 1, 'key': 'address1', 'operator': 'equal', 'value': '北海道'})
    filter2 = Filter(**{'id': 2, 'key': 'birthDate', 'operator': 'equal', 'value': '2010-10-10'})
    filters.append(filter1)
    filters.append(filter2)

    subject = Subject(**{'topics': topics, 'factors': factors, 'filters': filters, 'joins': joins})
    report = Report(**{'name': 'test_report', 'subject': subject})
    report.get_report_dataset()


def test_report():
    import_report_data()
    get_report_dataset()


test_report()
