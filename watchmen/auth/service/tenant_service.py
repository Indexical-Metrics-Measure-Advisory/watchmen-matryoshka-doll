from watchmen.auth.tenant import Tenant
from watchmen.database.storage import storage_template

TENANTS = "tenants"

def create(tenant: Tenant) -> Tenant:
    return storage_template.insert_one(tenant, Tenant, TENANTS)

def update(tenant: Tenant) -> Tenant:
    return storage_template.update_one(tenant, Tenant, TENANTS)


def query_by_code(tenant_code: str) -> Tenant:

    pass


def delete(tenant_id: str):
    pass

def load(tenant_id: str) -> Tenant:
    return storage_template.find_one({"tenantId":tenant_id}, Tenant, TENANTS)
