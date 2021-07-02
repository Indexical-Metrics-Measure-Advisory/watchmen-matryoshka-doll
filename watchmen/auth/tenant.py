from watchmen.common.watchmen_model import WatchmenModel


class Tenant(WatchmenModel):
    tenantId: str = None
    tenantCode: str = None
    tenantDescription: str = None


