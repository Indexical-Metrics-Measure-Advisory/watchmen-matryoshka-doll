from watchmen.auth.tenant import Tenant


def create(tenant: Tenant) -> Tenant:
    pass


def update(tenant: Tenant) -> Tenant:
    pass


def query_by_code(tenant_code: str) -> Tenant:
    pass


def delete(tenant_id: str):
    pass


def load(tenant_id: str) -> Tenant:
    pass
