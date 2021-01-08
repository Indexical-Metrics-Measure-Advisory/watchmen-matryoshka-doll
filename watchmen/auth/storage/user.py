from bson import regex

from watchmen.auth.user import User
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN, build_data_pages

# from watchmen.common.utils import pickle_wrapper

db = get_client(WATCHMEN)

users = db.get_collection('users')


def get_user(user_id: int):
    return users.find_one({"userId": user_id})


def create_user_storage(user: User):
    user.userId = get_surrogate_key()
    if type(user) is not dict:
        user = user.dict()
    users.insert_one(user)
    return user


def query_users_by_name_with_pagination(query_name: str, pagination: Pagination):
    items_count= users.find({"name": regex.Regex(query_name)}).count()
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = users.find({"name": regex.Regex(query_name)}).skip(skips).limit(pagination.pageSize)
    return build_data_pages(pagination,list(result),items_count)
