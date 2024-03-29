from model.model.common.data_page import DataPage

from watchmen.auth.tenant import Tenant
from watchmen.database.find_storage_template import find_storage_template

TENANTS = "tenants"

storage_template = find_storage_template()


def create(tenant: Tenant) -> Tenant:
    return storage_template.insert_one(tenant, Tenant, TENANTS)


def update(tenant: Tenant) -> Tenant:
    return storage_template.update_one(tenant, Tenant, TENANTS)


def query_by_name(tenant_name: str, pagination) -> DataPage:
    if tenant_name != '':
        query_dict = {"name": {"like": tenant_name}}
        sort_dict = [("lastModified", "desc")]
        return storage_template.page_(query_dict, sort_dict, pagination, Tenant, TENANTS)
    else:
        sort_dict = [("lastModified", "desc")]
    return storage_template.page_all(sort_dict, pagination, Tenant, TENANTS)


def delete(tenant_id: str):
    return storage_template.delete_by_id(tenant_id, Tenant, TENANTS)


def load(tenant_id: str) -> Tenant:
    return storage_template.find_one({"tenantId": tenant_id}, Tenant, TENANTS)
