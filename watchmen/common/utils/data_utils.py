import math
# import os
from enum import Enum

from model.model.common.data_page import DataPage
from model.model.common.user import SUPER_ADMIN, User
from pydantic.tools import lru_cache
from storage.model.data_source import DataSource

from watchmen.common.constants.parameter_constants import RAW
from watchmen.config.config import settings
from watchmen.pipeline.utils.units_func import ADDRESS, CONTINENT, REGION, COUNTRY, PROVINCE, CITY, \
    DISTRICT, ROAD, COMMUNITY, FLOOR, RESIDENCE_TYPE, RESIDENTIAL_AREA, TEXT, EMAIL, PHONE, MOBILE, FAX, GENDER, \
    HALF_YEAR, QUARTER, SEASON, MONTH, HALF_MONTH, TEN_DAYS, WEEK_OF_YEAR, WEEK_OF_MONTH, HALF_WEEK, DAY_OF_MONTH, \
    DAY_OF_WEEK, DAY_KIND, HOUR, HOUR_KIND, MINUTE, SECOND, AM_PM, DATETIME, UNSIGNED, DATE, SEQUENCE

WATCHMEN = "watchmen"
MONITOR = "monitor"


@lru_cache(maxsize=50)
def build_collection_name(topic_name):
    return "topic_" + topic_name


def is_field_value(value):
    return type(value) != dict and type(value) != list


def get_dict_schema_set(model_schema_set):
    result = {}
    for schema in model_schema_set.schemas.values():
        result[schema.modelId] = schema
    return result


def is_raw(topic):
    return topic.type == RAW


def get_id_name():
    if settings.STORAGE_ENGINE == "mongo":
        return "_id"
    elif settings.STORAGE_ENGINE == "oracle":
        return "id_"
    elif settings.STORAGE_ENGINE == "mysql":
        return "id_"


def get_id_name_by_datasource(datasource: DataSource):
    if datasource is None:
        return get_id_name()
    else:
        if datasource.dataSourceType == "mongodb":
            return "_id"
        elif datasource.dataSourceType == "oracle":
            return "id_"
        elif datasource.dataSourceType == "mysql":
            return "id_"


def get_dict_relationship(model_schema_set):
    result = {}
    for relationship in model_schema_set.relationships.values():
        if relationship.parentId in result.keys():
            result[relationship.parentId].append(relationship)
        else:
            result[relationship.parentId] = []
            result[relationship.parentId].append(relationship)
    return result


class RelationshipType(Enum):
    OneToOne = "OneToOne"
    OneToMany = "OneToMany"
    ManyToMany = "ManyToMany"


def build_data_pages(pagination, result, item_count):
    data_page = DataPage()
    data_page.data = result
    data_page.itemCount = item_count
    data_page.pageSize = pagination.pageSize
    data_page.pageNumber = pagination.pageNumber
    data_page.pageCount = math.ceil(item_count / pagination.pageSize)
    return data_page


def check_fake_id(id: str) -> bool:
    return id.startswith("f-")


def is_presto_varchar_type(factor_type):
    date_types = [ADDRESS, CONTINENT, REGION, COUNTRY, PROVINCE, CITY, DISTRICT, ROAD, COMMUNITY, FLOOR, RESIDENCE_TYPE,
                  RESIDENTIAL_AREA, TEXT, EMAIL, PHONE, MOBILE, FAX, GENDER]
    if factor_type in date_types:
        return True
    else:
        return False


def is_presto_int_type(factor_type):
    date_types = [HALF_YEAR, QUARTER, SEASON, MONTH, HALF_MONTH, TEN_DAYS, WEEK_OF_YEAR, WEEK_OF_MONTH, HALF_WEEK,
                  DAY_OF_MONTH, DAY_OF_WEEK,
                  DAY_KIND, HOUR, HOUR_KIND, MINUTE, SECOND, AM_PM, UNSIGNED, SEQUENCE]
    if factor_type in date_types:
        return True
    else:
        return False


def is_presto_datetime(factor_type):
    date_types = [DATETIME, DATE]
    if factor_type in date_types:
        return True
    else:
        return False


def convert_to_dict(instance):
    if type(instance) is not dict:
        return instance.dict(by_alias=True)
    else:
        return instance


def capital_to_lower(dict_info):
    new_dict = {}
    for i, j in dict_info.items():
        new_dict[i.lower()] = j
    return new_dict


def add_tenant_id_to_instance(instance, current_user: User = None):
    if current_user:
        instance["tenant_id_"] = current_user.tenantId
    return instance


def add_tenant_id_to_model(instance, user):
    if settings.DEFAULT_DATA_ZONE_ON:
        instance.tenantId = "1"
    else:
        instance.tenantId = user.tenantId

    return instance


def add_user_id_to_model(instance, user):
    if user:
        instance.userId = user.userId
    return instance


def compare_tenant(instance, user):
    if instance.tenantId == user.tenantId:
        return True
    else:
        return False


def is_superuser(user: User):
    if user.role == SUPER_ADMIN:
        return True
    else:
        return False


def is_super_admin(user):
    return user.role == "superadmin"


def clean_password(user_list):
    for user in user_list:
        user.password = None

    return user_list
