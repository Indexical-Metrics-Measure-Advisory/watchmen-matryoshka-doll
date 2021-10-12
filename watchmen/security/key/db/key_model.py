from typing import Dict

from watchmen.common.watchmen_model import WatchmenModel


class KeyStore(WatchmenModel):
    tenantId: str = None
    params: Dict = None
    keyType: str = None
