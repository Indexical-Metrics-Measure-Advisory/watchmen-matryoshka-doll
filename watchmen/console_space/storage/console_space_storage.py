from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.console_space.model.console_space import ConsoleSpace

db = get_client()
console_spaces = db.get_collection('console_spaces')
console_space_graph_collection = db.get_collection('console_space_graph')


def create_console_space(console_space: ConsoleSpace):
    console_spaces.insert(console_space.dict())
    return console_space


def update_console_space(console_space: ConsoleSpace):
    console_spaces.update_one({"connectId": console_space.connectId}, {"$set": console_space.dict()})
    return console_space


def save_console_space(console_space: ConsoleSpace):
    if console_space.connectId is None or check_fake_id(console_space.connectId):
        console_space.connectId = get_surrogate_key()
        return create_console_space(console_space)
    else:
        return update_console_space(console_space)


def load_console_space_by_id(connect_id: str):
    result = console_spaces.find_one({"connectId": connect_id})
    return ConsoleSpace.parse_obj(result)


def delete_console_space_storage(connect_id):
    console_spaces.delete_one({"connectId": connect_id})


def load_console_space_list_by_user(user_id):
    result = console_spaces.find({"userId": user_id})
    return list(result)


def load_console_space_by_subject_id(subject_id):
    result = console_spaces.find_one({"subjectIds": subject_id})
    return ConsoleSpace.parse_obj(result)


def rename_console_space_by_id(connect_id, name):
    console_spaces.update_one({"connectId": connect_id}, {"$set": {"name": name}})


def create_console_space_graph(console_space_graph):
    console_space_graph_collection.insert(console_space_graph.dict())


def update_console_space_graph(console_space_graph):
    console_space_graph_collection.update_one({"connectId": console_space_graph.connectId},
                                              {"$set": console_space_graph.dict()})


def load_console_space_graph_by_user_id(user_id):
    result = console_space_graph_collection.find({"userId": user_id})
    return list(result)


def load_console_space_graph(connect_id):
    result = console_space_graph_collection.find_one({"connectId": connect_id})
    return result


def import_console_spaces(console_space):
    console_spaces.insert_one(console_space.dict())
