from storage.common.data_page import DataPage
from storage.config.config import settings

MYSQL = "mysql"
MONGO = "mongo"
ORACLE = "oracle"


def create_raw_pipeline_monitor():
    if settings.STORAGE_ENGINE == ORACLE:
        from watchmen.common.oracle.monitor import oracle_monitor
        oracle_monitor.create_raw_pipeline_monitor()



def raw_pipeline_monitor_page_(where, sort, pageable, model, name) -> DataPage:
    pass



