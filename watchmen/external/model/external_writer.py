from watchmen.common.watchmen_model import WatchmenModel


class ExternalWriter(WatchmenModel):
    writerId: str = None
    writerCode: str = None
    type: str = None
    pat: str = None
    url: str = None
    tenantId: str = None
