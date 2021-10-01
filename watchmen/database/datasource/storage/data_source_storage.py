from watchmen.common.model.user import User
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.config.config import settings
from watchmen.database.datasource.data_source import DataSource
from watchmen.database.storage.storage_template import page_, find_one, insert_one, update_one, page_all, \
    list_all, find_

DATA_SOURCES = "data_sources"


def save_data_source(data_source: DataSource, current_user: User = None):
    if check_fake_id(data_source.dataSourceId):
        data_source.dataSourceId = get_surrogate_key()
        return insert_one(data_source, DataSource, DATA_SOURCES)
    else:
        return update_one(data_source, DataSource, DATA_SOURCES)


def load_data_source_by_id(data_source_id: str, current_user: User = None):
    return find_one({"dataSourceId": data_source_id}, DataSource, DATA_SOURCES)


def load_data_source_list(current_user: User):
    if settings.MULTIPLE_DATA_SOURCE:
        return find_({"tenantId": current_user.tenantId}, DataSource, DATA_SOURCES)
    else:
        return list_all(DataSource, DATA_SOURCES)


def list_all_data_source_list():
    return list_all(DataSource, DATA_SOURCES)


def load_data_source_list_with_pagination(query_name: str, pagination: Pagination, current_user):
    if query_name != '':
        query_dict = {"name": {"like": query_name}}
        sort_dict = [("lastModified", "desc")]
        return page_(query_dict, sort_dict, pagination, DataSource, DATA_SOURCES)
    else:
        sort_dict = [("lastModified", "desc")]
        return page_all(sort_dict, pagination, DataSource, DATA_SOURCES)
