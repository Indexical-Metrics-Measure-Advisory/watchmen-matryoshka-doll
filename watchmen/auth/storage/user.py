from watchmen.auth.user import User
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key

from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN
# from watchmen.common.utils import pickle_wrapper

db = get_client(WATCHMEN)

users = db.get_collection('users')


def get_user(client,id):
    return User(username="admin")


def create_user(user:User):
    user.userId = get_surrogate_key()
    if type(user) is not dict:
        user = user.dict()
    return user.userId


def query_users_by_name_with_pagination(query_name:str,pagination: Pagination):


    pass



