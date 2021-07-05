from watchmen.auth.service.security import get_password_hash

from watchmen.auth.user import User
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
# db = get_client()
#
# users = db.get_collection('users')
from watchmen.common.utils.data_utils import is_superuser
from watchmen.database.storage.storage_template import find_one, find_, insert_one, update_one, page_
from watchmen.database.storage.storage_template import find_template

USERS = "users"

template = find_template()


def __clean_password(user):
    if user is None:
        return  None
    else:
        user.password = None
        return user


def get_user(user_id):
    user =  find_one({"userId": user_id}, User, USERS)
    return __clean_password(user)


def get_user_list_by_ids(user_ids: list, current_user):
    return find_({"and": [{"userId": {"in": user_ids}}, {"tenantId": current_user.tenantId}]}, User, USERS)


def load_user_list_by_name(query_name, current_user):
    return find_({"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}, User, USERS)


def load_user_by_name(user_name) -> User:
    return find_one({"name": user_name}, User, USERS)


def create_user_storage(user: User):
    user.userId = get_surrogate_key()
    user.password = get_password_hash(user.password)
    return insert_one(user, User, USERS)


def update_user_storage(user: User):
    if user.password is not None:
        user.password = get_password_hash(user.password)

    return update_one(user, User, USERS)


def query_users_by_name_with_pagination(query_name: str, pagination: Pagination, current_user=None):
    if is_superuser(current_user.name):
        where_ = {"name": {"like": query_name}}
    else:
        where_ = {"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}
    return page_(where_, [("name", "desc")],
                 pagination, User, USERS)


def import_user_to_db(user):
    # template.create(USERS, user, User)
    return insert_one(user, User, USERS)
