from watchmen.auth.user import User
from watchmen.database.topic.adapter.topic_storage_adapter import get_template_by_datasource_id
from watchmen.topic.topic import Topic


def __merge_tenant_id_to_where_condition(where_,current_user:User = None):
    if current_user:
        where_["tenant_id_"] = current_user.tenantId
    return where_


def query_topic_data(where_, topic: Topic,current_user:User ):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_find_one(__merge_tenant_id_to_where_condition(where_,current_user), topic.name)


def query_multiple_topic_data(where_, topic: Topic,current_user:User):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_find_(__merge_tenant_id_to_where_condition(where_,current_user), topic.name)


def query_topic_data_aggregate(where_, aggregate, topic: Topic,current_user:User ):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_find_with_aggregate(__merge_tenant_id_to_where_condition(where_,current_user), topic.name, aggregate)
