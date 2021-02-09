from bson import regex

from watchmen.auth.service.security import get_password_hash
from watchmen.auth.user import User
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_data_pages

db = get_client()

users = db.get_collection('users')


def get_user(user_id):
    user = users.find_one({"userId": user_id})
    return User.parse_obj(user)


def get_user_list_by_ids(user_ids: list):
    result = users.find({"userId": {"$in": user_ids}})
    return list(result)


def load_user_list_by_name(query_name):
    result = users.find({"name": regex.Regex(query_name)})
    return list(result)


def load_user_by_name(user_name):
    return users.find_one({"name": user_name})


def create_user_storage(user: User):
    if user.userId is None:
        user.userId = get_surrogate_key()
    user.password = get_password_hash(user.password)
    if type(user) is not dict:
        user = user.dict()
    users.insert_one(user)
    return user


def update_user_storage(user: User):
    users.update_one({"userId": user.userId}, {"$set": user.dict()})
    return user


def query_users_by_name_with_pagination(query_name: str, pagination: Pagination):
    items_count = users.find({"name": regex.Regex(query_name)}).count()
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = users.find({"name": regex.Regex(query_name)}).skip(skips).limit(pagination.pageSize)
    return build_data_pages(pagination, list(result), items_count)
