from watchmen.common.watchmen_model import WatchmenModel


class KeyStore(WatchmenModel):
    tenantId: str = None
    keyId: str = None
    keyToken: str = None


def load_key_store_by_tenant(tenant_id: str) -> KeyStore:
    pass
