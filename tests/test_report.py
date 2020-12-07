from watchmen.storage.topic_data_storage import save_topic_instances
from watchmen.storage.topic_data_storage import save_topic_instance
import json
import os


def import_report_data():
    os.chdir('D:/')
    # Reading the json as a dict, policy information
    with open('test1.json') as json_data:
        policy_data = json.load(json_data, encoding='utf-8')

    # import policy data in master topic
    save_topic_instances('test_report_policy_data_col', policy_data)

    # Reading the json as a dict, customer information
    with open('customer_test.json') as json_data:
        customer_data = json.load(json_data, encoding='utf-8')

    # import customer data in master topic
    save_topic_instance('test_report_customer_data_col', customer_data)


def test_report():
    #import_report_data()
    pass

test_report()