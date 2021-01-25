from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client, get_client_db
from watchmen.common.utils.data_utils import WATCHMEN
from watchmen.console_space.model.console_space import ConsoleSpaceGroup

db = get_client()
# print("create_console_group_to_storage",db.client)


GROUP_COLLECTION='console_space_group'
console_space_group = db.get_collection('console_space_group')


# def __get_group_collection():
#     return client[WATCHMEN].get_collection(GROUP_COLLECTION)


def create_console_group_to_storage(group: ConsoleSpaceGroup):
    with get_client_db() as client:
        group.groupId = get_surrogate_key()
        client[WATCHMEN].get_collection(GROUP_COLLECTION).insert_one(group.dict())
        return ConsoleSpaceGroup.parse_obj(group)


def load_console_group_by_id(group_id):
    result = console_space_group.find_one({"groupId": group_id})
    return ConsoleSpaceGroup.parse_obj(result)


def update_console_group(group: ConsoleSpaceGroup):
    console_space_group.update_one({"groupId": group.groupId}, {"$set": group.dict()})
    return group


def load_console_group_list_by_ids(group_ids):
    group = console_space_group.find({"groupId": {"$in": group_ids}})
    return list(group)


def rename_console_group_by_id(group_id, name):
    console_space_group.update_one({"groupId": group_id}, {"$set": {"name": name}})
