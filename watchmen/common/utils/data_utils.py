
from enum import Enum


from watchmen.pipeline.single.stage.unit.utils.units_func import ADDRESS, CONTINENT, REGION, COUNTRY, PROVINCE, CITY, \
    DISTRICT, ROAD, COMMUNITY, FLOOR, RESIDENCE_TYPE, RESIDENTIAL_AREA, TEXT, EMAIL, PHONE, MOBILE, FAX, GENDER, \
    HALF_YEAR, QUARTER, SEASON, MONTH, HALF_MONTH, TEN_DAYS, WEEK_OF_YEAR, WEEK_OF_MONTH, HALF_WEEK, DAY_OF_MONTH, \
    DAY_OF_WEEK, DAY_KIND, HOUR, HOUR_KIND, MINUTE, SECOND, AM_PM, DATETIME, UNSIGNED, DATE, SEQUENCE

WATCHMEN = "watchmen"
MONITOR = "monitor"




def is_field_value(value):
    return type(value) != dict and type(value) != list


def get_dict_schema_set(model_schema_set):
    result = {}
    for schema in model_schema_set.schemas.values():
        result[schema.modelId] = schema
    return result


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


