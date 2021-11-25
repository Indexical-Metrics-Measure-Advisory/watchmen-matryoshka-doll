from model.model.common.pagination import Pagination
from model.model.common.user import User

from watchmen.auth.service.security import get_password_hash
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import is_superuser
from watchmen.database.find_storage_template import find_storage_template

USERS = "users"

storage_template = find_storage_template()


# template = find_template()


def __clean_password(user):
    if user is None:
        return None
    else:
        user.password = None
        return user


def get_user(user_id) -> User:
    user = storage_template.find_one({"userId": user_id}, User, USERS)
    return __clean_password(user)


"""
def get_user_list_by_ids(user_ids: list, current_user):
    return find_({"and": [{"userId": {"in": user_ids}}, {"tenantId": current_user.tenantId}]}, User, USERS)
"""


def get_user_list_by_ids(user_ids: list, current_user):
    if user_ids:
        return storage_template.find_({"and": [{"userId": {"in": user_ids}}, {"tenantId": current_user.tenantId}]},
                                      User, USERS)
    else:
        return []


def load_user_list_by_name(query_name, current_user):
    return storage_template.find_({"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}, User,
                                  USERS)


def load_user_by_name(user_name) -> User:
    return storage_template.find_one({"name": user_name}, User, USERS)


def create_user_storage(user: User):
    user.userId = get_surrogate_key()
    user.password = get_password_hash(user.password)
    return storage_template.insert_one(user, User, USERS)


def update_user_storage(user: User):
    return storage_template.update_one(user, User, USERS)


def query_users_by_name_with_pagination(query_name: str, pagination: Pagination, current_user=None):
    if is_superuser(current_user):
        where_ = {"name": {"like": query_name}}
    else:
        where_ = {"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}
    return storage_template.page_(where_, [("name", "desc")],
                                  pagination, User, USERS)


def import_user_to_db(user):
    return storage_template.insert_one(user, User, USERS)
