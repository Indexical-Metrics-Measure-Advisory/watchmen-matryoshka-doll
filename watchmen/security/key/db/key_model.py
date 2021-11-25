from typing import Dict

from model.model.common.watchmen_model import WatchmenModel


class KeyStore(WatchmenModel):
    tenantId: str = None
    params: Dict = None
    keyType: str = None
