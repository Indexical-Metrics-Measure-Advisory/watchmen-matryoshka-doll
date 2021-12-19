from typing import List

from model.model.common.user import User
from model.model.console_space.connect_space_graphics import ConnectedSpaceGraphics
from model.model.console_space.console_space import ConsoleSpace

from watchmen_boot.guid.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.database.find_storage_template import find_storage_template

CONSOLE_SPACES = "console_spaces"

storage_template = find_storage_template()


def create_console_space(console_space: ConsoleSpace):
    return storage_template.insert_one(console_space, ConsoleSpace, CONSOLE_SPACES)


def update_console_space(console_space: ConsoleSpace):
    return storage_template.update_one_first({"connectId": console_space.connectId}, console_space, ConsoleSpace,
                                             CONSOLE_SPACES)


def save_console_space(console_space: ConsoleSpace) -> ConsoleSpace:
    if console_space.connectId is None or check_fake_id(console_space.connectId):
        console_space.connectId = get_surrogate_key()
        return create_console_space(console_space)
    else:
        return update_console_space(console_space)


def load_console_space_by_id(connect_id: str, current_user) -> ConsoleSpace:
    return storage_template.find_one({"and": [{"connectId": connect_id}, {"tenantId": current_user.tenantId}]},
                                     ConsoleSpace,
                                     CONSOLE_SPACES)


def load_template_space_list_by_space_id(space_id) -> List[ConsoleSpace]:
    return storage_template.find_({"and": [{"spaceId": space_id}, {"isTemplate": True}]}, ConsoleSpace,
                                  CONSOLE_SPACES)


def delete_console_space_storage(connect_id: str):
    # template.delete_one("console_spaces", {"connectId": connect_id})
    storage_template.delete_by_id(connect_id, "console_spaces")


def load_console_space_list_by_user(user_id: str, current_user: User) -> ConsoleSpace:
    return storage_template.find_({"and": [{"userId": user_id}, {"tenantId": current_user.tenantId}]}, ConsoleSpace,
                                  CONSOLE_SPACES)


def load_console_space_template_list_by_user(user_id: str, current_user: User) -> ConsoleSpace:
    return storage_template.find_(
        {"and": [{"userId": user_id}, {"tenantId": current_user.tenantId}, {"isTemplate": True}]},
        ConsoleSpace, CONSOLE_SPACES)


def load_console_space_by_subject_id(subject_id: str, current_user) -> ConsoleSpace:
    return storage_template.find_one({"subjectIds": {"in": [subject_id]}}, ConsoleSpace,
                                     CONSOLE_SPACES)


def rename_console_space_by_id(connect_id: str, name: str) -> ConsoleSpace:
    # return template.update_one("console_spaces", {"connectId": connect_id}, {"name": name}, ConsoleSpace)
    return storage_template.update_one_first({"connectId": connect_id}, {"name": name}, ConsoleSpace, CONSOLE_SPACES)


def create_console_space_graph(console_space_graph: ConnectedSpaceGraphics) -> ConnectedSpaceGraphics:
    # return template.create("console_space_graph", console_space_graph, ConnectedSpaceGraphics)
    return storage_template.insert_one(console_space_graph, ConnectedSpaceGraphics, "console_space_graph")


def update_console_space_graph(console_space_graph: ConnectedSpaceGraphics) -> ConnectedSpaceGraphics:
    return storage_template.update_one_first({"connectId": console_space_graph.connectId}, console_space_graph,
                                             ConnectedSpaceGraphics,
                                             "console_space_graph")


def load_console_space_graph_by_user_id(user_id: str, current_user) -> List[ConnectedSpaceGraphics]:

    return storage_template.list_({"and": [{"userId": user_id}, {"tenantId": current_user.tenantId}]},
                                  ConnectedSpaceGraphics,
                                  "console_space_graph")


def load_console_space_graph(connect_id: str, current_user) -> ConnectedSpaceGraphics:
    # return template.find_one("console_space_graph", {"connectId": connect_id}, ConnectedSpaceGraphics)
    return storage_template.find_one({"and": [{"connectId": connect_id}, {"tenantId": current_user.tenantId}]},
                                     ConnectedSpaceGraphics,
                                     "console_space_graph")


def import_console_space_to_db(console_space: ConsoleSpace) -> ConsoleSpace:
    # return template.create("console_space_graph", console_space, ConnectedSpaceGraphics)
    return storage_template.insert_one(console_space, ConsoleSpace, CONSOLE_SPACES)
