
from watchmen.storage.engine.storage_engine import get_client

# WATCHMEN = "watchmen"
from watchmen.utils.data_utils import WATCHMEN

client = get_client(WATCHMEN)


def save_topic_instance(topic_name, instance):
    topic_instance_col = client.get_collection(topic_name)
    with client.start_session() as s:
        s.start_transaction()
        topic_instance_col.insert_one(instance)
        s.commit_transaction()


def save_topic_instances(topic_name, instances):
    topic_instance_col = client.get_collection(topic_name)
    topic_instance_col.insert_many(instances)


def get_topic_instances(topic_name, **conditions):
    print(topic_name)
    topic_instance_col = client.get_collection(topic_name)
    return topic_instance_col.find(conditions)

#conditions = {"topicId": "customer"}

conditions = {"attr.CustomerName": "andy wen"}

print(get_topic_instances("customer", **conditions).next())