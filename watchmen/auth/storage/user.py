from watchmen.auth.service.security import get_password_hash
from watchmen.auth.user import User
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine_adaptor import find_template

# db = get_client()
#
# users = db.get_collection('users')
from watchmen.common.storage.storage_template import find_one, find_by_id, find_, insert_one, update_one, page_

USERS = "users"

template = find_template()


def get_user(user_id):
    # user = users.find_one({"userId": user_id})
    # if user is None:
    #     return None
    # else:
    #     return User.parse_obj(user)
    # return template.find_one(USERS, {"userId": user_id}, User)
    return find_by_id(user_id, User, USERS)


def get_user_list_by_ids(user_ids: list):
    # result = users.find({"userId": {"$in": user_ids}})
    # return list(result)
    # return template.find(USERS, {"userId": {"$in": user_ids}}, User)
    return find_({"userId": {"in": user_ids}}, User, USERS)


def load_user_list_by_name(query_name):
    # result = users.find({"name": regex.Regex(query_name)})
    # return list(result)
    # return template.find(USERS, {"name": regex.Regex(query_name)}, User)
    return find_({"name": {"like": query_name}}, User, USERS)




def load_user_by_name(user_name):
    # return users.find_one({"name": user_name})
    # return template.find_one(USERS, {"name": user_name}, User)
    return find_one({"name": user_name}, User, USERS)


def create_user_storage(user: User):
    if user.userId is None:
        user.userId = get_surrogate_key()
    user.password = get_password_hash(user.password)
    # return template.create(USERS, user, User)
    return insert_one(user, User, USERS)


def update_user_storage(user: User):
    # return template.update_one(USERS, {"userId": user.userId}, user, User)
    return update_one(user, User, USERS)


def query_users_by_name_with_pagination(query_name: str, pagination: Pagination):
    # return template.query_with_pagination(USERS, pagination, User, {"name": regex.Regex(query_name)})
    return page_({"name": {"like": query_name}}, [("name", "desc")], pagination, User, USERS)


def import_user_to_db(user):
    # template.create(USERS, user, User)
    return insert_one(user, User, USERS)
