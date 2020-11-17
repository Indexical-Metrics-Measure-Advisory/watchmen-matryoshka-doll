from watchmen.master.master_schema import MasterSchema
from watchmen.storage.master_storage import save_master_space, update_master_space, load_master_space_by_name
from watchmen.storage.topic_schema_storage import save_topic


def add_topic_to_master():
    pass


def remove_from_master():
    pass


def update_topic_to_master():
    pass


def load_master_space(space_name):
    return load_master_space_by_name(space_name)


def add_factor_to_master_topic():
    pass


def create_master_space(user,domain):
    master_space = MasterSchema()
    master_space.user = user
    master_space.name = user+"_"+domain
    # save_master_space(master_space)
    # master_space.id = inserted_id
    return master_space


def add_topic_to_master_space(topic, master_space):
    master_space.topic_list.append(topic)
    update_master_space(master_space)


def add_topic_list_to_master(topic_list, master_space):

    topic_id_list =[]
    for topic in topic_list:
        insert_id =str(save_topic(topic.dict()).inserted_id)
        topic_id_list.append(insert_id)

    print(topic_id_list)
    master_space.topic_id_list = topic_id_list
    save_master_space(master_space).inserted_id
    # master_space.id = inserted_id
    return master_space


def get_summary_for_master_space(master_space):
    return master_space
