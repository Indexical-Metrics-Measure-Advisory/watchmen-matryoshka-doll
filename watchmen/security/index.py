import logging

from watchmen.common.security.algorithm_service import find_algorithm_encryption
from watchmen.security.factor.index import is_security_scope
from watchmen.security.key.db.index import load_key_store_by_tenant

log = logging.getLogger("app." + __name__)


def encrypt_value(factor_type, factor_encrypt, value_, tenant_id):
    if is_security_scope(factor_type):
        algorithm = find_algorithm_encryption(factor_type,factor_encrypt)
        key_store = load_key_store_by_tenant(tenant_id)
        if key_store is None:
            return algorithm(value_, {})
        else:
            return algorithm(value_,key_store.params)
    else:
        log.error("factor_type is not supported for encrypt :{}".format(factor_type))
