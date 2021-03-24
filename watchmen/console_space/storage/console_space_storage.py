from typing import List

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.console_space.model.connect_space_graphics import ConnectedSpaceGraphics
from watchmen.console_space.model.console_space import ConsoleSpace

template = find_template()


def create_console_space(console_space: ConsoleSpace):
    return template.create("console_spaces", console_space, ConsoleSpace)


def update_console_space(console_space: ConsoleSpace):
    return template.update_one("console_spaces", {"connectId": console_space.connectId}, console_space, ConsoleSpace)


def save_console_space(console_space: ConsoleSpace) -> ConsoleSpace:
    if console_space.connectId is None or check_fake_id(console_space.connectId):
        console_space.connectId = get_surrogate_key()
        return create_console_space(console_space)
    else:
        return update_console_space(console_space)


def load_console_space_by_id(connect_id: str) -> ConsoleSpace:
    return template.find_one("console_spaces", {"connectId": connect_id}, ConsoleSpace)


def delete_console_space_storage(connect_id:str):
    template.delete_one("console_spaces", {"connectId": connect_id})


def load_console_space_list_by_user(user_id:str) -> ConsoleSpace:
    return template.find("console_spaces", {"userId": user_id}, ConsoleSpace)


def load_console_space_by_subject_id(subject_id:str) -> ConsoleSpace:
    return template.find_one("console_spaces", {"subjectIds": subject_id}, ConsoleSpace)


def rename_console_space_by_id(connect_id:str, name:str) -> ConsoleSpace:
    return template.update_one("console_spaces", {"connectId": connect_id}, {"name": name}, ConsoleSpace)


def create_console_space_graph(console_space_graph:ConnectedSpaceGraphics) -> ConnectedSpaceGraphics:
    return template.create("console_space_graph", console_space_graph, ConnectedSpaceGraphics)


def update_console_space_graph(console_space_graph:ConnectedSpaceGraphics) -> ConnectedSpaceGraphics:
    return template.update_one("console_space_graph", {"connectId": console_space_graph.connectId}, console_space_graph,
                               ConnectedSpaceGraphics)


def load_console_space_graph_by_user_id(user_id:str) -> List[ConnectedSpaceGraphics]:
    return template.find("console_space_graph", {"userId": user_id}, ConnectedSpaceGraphics)


def load_console_space_graph(connect_id:str) -> ConnectedSpaceGraphics:
    return template.find_one("console_space_graph", {"connectId": connect_id}, ConnectedSpaceGraphics)


def import_console_spaces(console_space:ConnectedSpaceGraphics) -> ConnectedSpaceGraphics:
    return template.create("console_space_graph", console_space, ConnectedSpaceGraphics)
