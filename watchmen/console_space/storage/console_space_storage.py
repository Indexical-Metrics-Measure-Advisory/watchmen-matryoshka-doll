from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.console_space.model.connect_space_graphics import ConnectedSpaceGraphics
from watchmen.console_space.model.console_space import ConsoleSpace

#
# db = get_client()
# console_spaces = db.get_collection('console_spaces')
# console_space_graph_collection = db.get_collection('console_space_graph')

template = find_template()


def create_console_space(console_space: ConsoleSpace):
    return template.create("console_spaces", console_space, ConsoleSpace)


def update_console_space(console_space: ConsoleSpace):
    # console_spaces.update_one({"connectId": console_space.connectId}, {"$set": console_space.dict()})
    # return console_space
    return template.update_one("console_spaces", {"connectId": console_space.connectId}, console_space, ConsoleSpace)


def save_console_space(console_space: ConsoleSpace):
    if console_space.connectId is None or check_fake_id(console_space.connectId):
        console_space.connectId = get_surrogate_key()
        return create_console_space(console_space)
    else:
        return update_console_space(console_space)


def load_console_space_by_id(connect_id: str):
    # result = console_spaces.find_one({"connectId": connect_id})
    # if result is None:
    #     return None
    # else:
    #     return ConsoleSpace.parse_obj(result)

    return template.find_one("console_spaces", {"connectId": connect_id}, ConsoleSpace)


def delete_console_space_storage(connect_id):
    # console_spaces.delete_one({"connectId": connect_id})
    template.delete_one("console_spaces", {"connectId": connect_id})


def load_console_space_list_by_user(user_id):
    # result = console_spaces.find({"userId": user_id})
    # return list(result)
    return template.find("console_spaces", {"userId": user_id}, ConsoleSpace)


def load_console_space_by_subject_id(subject_id):
    # result = console_spaces.find_one({"subjectIds": subject_id})
    # return ConsoleSpace.parse_obj(result)
    return template.find_one("console_spaces", {"subjectIds": subject_id}, ConsoleSpace)


def rename_console_space_by_id(connect_id, name):
    # console_spaces.update_one({"connectId": connect_id}, {"$set": {"name": name}})
    return template.update_one("console_spaces", {"connectId": connect_id}, {"name": name}, ConsoleSpace)


def create_console_space_graph(console_space_graph):
    return template.create("console_space_graph", console_space_graph, ConnectedSpaceGraphics)
    # console_space_graph_collection.insert(console_space_graph.dict())


def update_console_space_graph(console_space_graph):
    # console_space_graph_collection.update_one({"connectId": console_space_graph.connectId},
    #                                           {"$set": console_space_graph.dict()})

    return template.update_one("console_space_graph", {"connectId": console_space_graph.connectId}, console_space_graph,
                               ConnectedSpaceGraphics)


def load_console_space_graph_by_user_id(user_id):
    # result = console_space_graph_collection.find({"userId": user_id})
    # return list(result)
    return template.find("console_space_graph", {"userId": user_id}, ConnectedSpaceGraphics)


def load_console_space_graph(connect_id):
    # result = console_space_graph_collection.find_one({"connectId": connect_id})
    # return result
    return template.find_one("console_space_graph", {"connectId": connect_id}, ConnectedSpaceGraphics)


def import_console_spaces(console_space):
    return template.create("console_space_graph", console_space, ConnectedSpaceGraphics)
