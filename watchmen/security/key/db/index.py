from watchmen_boot.cache.cache_manage import cacheman
from watchmen.database.find_storage_template import find_storage_template

from watchmen.security.key.db.key_model import KeyStore

KEY_STORES = "key_stores"

storage_template = find_storage_template()


def load_key_store_by_tenant(tenant_id: str) -> KeyStore:
    cached_key = cacheman[KEY_STORES].get(tenant_id)
    if cached_key is not None:
        return cached_key
    else:
        result = storage_template.find_one({"tenantId": tenant_id}, KeyStore, KEY_STORES)
        cacheman[KEY_STORES].set(tenant_id, result)
    return result
