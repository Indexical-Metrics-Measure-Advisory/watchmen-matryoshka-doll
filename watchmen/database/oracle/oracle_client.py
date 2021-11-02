import json
import logging
from typing import List

import cx_Oracle
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from watchmen.common.utils.date_utils import DateTimeEncoder
from watchmen.config.config import settings
from watchmen.database.datasource.data_source import DataSource, DataSourceParam

SID = "SID"
SERVICE_NAME = "SERVICE_NAME"
log = logging.getLogger("app." + __name__)


class OracleEngine(object):

    cx_Oracle.init_oracle_client(lib_dir=settings.ORACLE_LIB_DIR)

    def find_sid(self, params: List[DataSourceParam]):
        for param in params:
            if param.name == SID:
                return param.value

    def find_service_name(self, params: List[DataSourceParam]):
        for param in params:
            if param.name == SERVICE_NAME.lower():
                return param.value

    def __init__(self, database: DataSource):
        sid = self.find_sid(database.params)
        if sid:
            dsn = cx_Oracle.makedsn(database.host,
                                    database.port, sid=sid)

        service_name = self.find_service_name(database.params)
        if sid is None and service_name is not None:
            dsn = cx_Oracle.makedsn(database.host,
                                    database.port, service_name=service_name)

        pool = cx_Oracle.SessionPool(
            database.username, database.password, dsn=dsn,
            min=3, max=3, increment=0, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT
        )

        self.engine = create_engine("oracle+cx_oracle://", creator=pool.acquire,
                                    poolclass=NullPool, coerce_to_decimal=False, echo=False, optimize_limits=True,
                                    future=True)

    def get_engine(self):
        return self.engine
