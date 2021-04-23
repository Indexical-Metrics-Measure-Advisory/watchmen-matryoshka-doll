from typing import List

from watchmen.auth.storage.user_group import get_user_group_list_by_ids, update_user_group_storage, USER_GROUPS
## TODO
from watchmen.common.mongo.mongo_template import update_many
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import insert_space_to_storage, load_space_by_name, update_space_to_storage


def create_space(space: Space) -> Space:
    if space.spaceId is None or check_fake_id(space.spaceId):
        space.spaceId = get_surrogate_key()
    if type(space) is not dict:
        space = space.dict()
    return insert_space_to_storage(space)


def update_space_by_id(space_id: str, space: Space) -> Space:
    if type(space) is not dict:
        space = space.dict()
    return update_space_to_storage(space_id, space)


def load_space(name: str) -> List[Space]:
    return load_space_by_name(name)


def sync_space_to_user_group(space: Space):
    ## TODO mongo
    update_many(collection_name=USER_GROUPS, query_dict={"spaceIds": {"$in": [space.spaceId]}},
                update_dict={"$pull": {"spaceIds": {"$in": [space.spaceId]}}})
    user_group_list = get_user_group_list_by_ids(space.groupIds)
    for user_group in user_group_list:
        if space.spaceId not in user_group.spaceIds:
            user_group.spaceIds.append(space.spaceId)
            update_user_group_storage(user_group)
