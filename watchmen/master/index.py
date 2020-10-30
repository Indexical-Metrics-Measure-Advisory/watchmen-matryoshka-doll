from watchmen.master.master_schema import MasterSchema
from watchmen.storage.master_storage import save_master_space, update_master_space


def add_topic_to_master():
    pass


def remove_from_master():
    pass


def update_topic_to_master():
    pass


def load_master_space():
    pass


def add_factor_to_master_topic():
    pass


def create_master_space(user):
    master_space = MasterSchema()
    master_space.user = user
    # inserted_id = save_master_space(master_space).inserted_id
    # master_space.id = inserted_id
    return master_space


def add_topic_to_master_space(topic, master_space):
    master_space.topic_list.append(topic)
    update_master_space(master_space)


def add_topic_list_to_master(topic_list, master_space):
    master_space.topic_list = topic_list
    inserted_id = save_master_space(master_space).inserted_id
    master_space.id = inserted_id
    return master_space


def get_summary_for_master_space(master_space):
    return master_space
