from model.model.common.watchmen_model import WatchmenModel


class Tenant(WatchmenModel):
    tenantId: str = None
    name: str = None
