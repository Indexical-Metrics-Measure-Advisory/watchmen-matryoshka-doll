from watchmen.database.find_storage_template import find_storage_template
from watchmen.topic.index.factor_index import FactorIndex

FACTOR_INDEX = "factor_index"

storage_template = find_storage_template()


def create_factor_index_to_storage(factor_index: FactorIndex):
    return storage_template.insert_one(factor_index, FactorIndex, FACTOR_INDEX)


def update_factor_index_to_storage(factor_index: FactorIndex):
    return storage_template.update_one_first({"and": [{"factorid": factor_index.factorId},
                                                      {"topicid": factor_index.topicId},
                                                      {"tenantid": factor_index.tenantId}]}, factor_index,FactorIndex,
                                             FACTOR_INDEX)


def delete_factor_index(factor_index: FactorIndex):
    return storage_template.delete_one({"and": [{"factorid": factor_index.factorId},
                                                {"topicid": factor_index.topicId},
                                                {"tenantid": factor_index.tenantId}]}, FACTOR_INDEX)


def load_factor_index_by_topic(topic_id: str, tenant_id):
    return storage_template.find_({"and": [{"topicid": topic_id},
                                           {"tenantid": tenant_id}]},FactorIndex,FACTOR_INDEX)



def load_factor_index_by_factor_name(name: str, tenant_id: str):
    return storage_template.find_({"and": [{"name":{"like":name} },
                                           {"tenantid": tenant_id}]}, FactorIndex, FACTOR_INDEX)


def load_factor_index_by_topic_name(name: str, tenant_id: str):
    return storage_template.find_({"and": [{"topicname": {"like": name}},
                                           {"tenantid": tenant_id}]}, FactorIndex, FACTOR_INDEX)