from watchmen.auth.storage.user import USERS, get_user_list_by_ids, update_user_storage
from watchmen.auth.user import User
from watchmen.auth.user_group import UserGroup

from watchmen.database.storage.storage_template import pull_update
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import get_space_list_by_ids, update_space_to_storage, SPACES


def sync_user_group_to_space(user_group: UserGroup,current_user):
    pull_update({"groupIds": {"in": [user_group.userGroupId]}}, {"groupIds": {"in": [user_group.userGroupId]}}, Space,
                SPACES)
    space_list = get_space_list_by_ids(user_group.spaceIds,current_user)
    for space in space_list:
        if space.groupIds is None:
            space.groupIds = []
        if user_group.userGroupId not in space.groupIds:
            space.groupIds.append(user_group.userGroupId)
            update_space_to_storage(space.spaceId, space)


def sync_user_group_to_user(user_group: UserGroup,current_user):
    pull_update({"groupIds": {"in": [user_group.userGroupId]}}, {"groupIds": {"in": [user_group.userGroupId]}}, User,
                USERS)
    user_list = get_user_list_by_ids(user_group.userIds,current_user)
    for user in user_list:
        if user.groupIds is None:
            user.groupIds = []
        if user_group.userGroupId not in user.groupIds:
            user.groupIds.append(user_group.userGroupId)
            update_user_storage(user)
