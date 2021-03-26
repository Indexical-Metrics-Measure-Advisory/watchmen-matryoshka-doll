from watchmen.auth.storage.user import USERS, get_user_list_by_ids, update_user_storage
from watchmen.auth.user_group import UserGroup
from watchmen.common.mongo.mongo_template import  update_many
from watchmen.space.storage.space_storage import get_space_list_by_ids, update_space_to_storage, SPACES


def sync_user_group_to_space(user_group: UserGroup):
    update_many(collection_name=SPACES, query_dict={"groupIds": {"$in": [user_group.userGroupId]}},
                update_dict={"$pull": {"groupIds": {"$in": [user_group.userGroupId]}}})
    # print(result)
    space_list = get_space_list_by_ids(user_group.spaceIds)
    for space in space_list:
        if user_group.userGroupId not in space.groupIds:
            space.groupIds.append(user_group.userGroupId)
            update_space_to_storage(space.spaceId, space)


def sync_user_group_to_user(user_group:UserGroup):
    result = update_many(collection_name=USERS, query_dict={"groupIds": {"$in": [user_group.userGroupId]}},
                update_dict={"$pull": {"groupIds": {"$in": [user_group.userGroupId]}}})

    print(result)

    # print()

    user_list = get_user_list_by_ids(user_group.userIds)
    for user in user_list:
        if user_group.userGroupId not in user.groupIds:
            user.groupIds.append(user_group.userGroupId)
            update_user_storage(user)



