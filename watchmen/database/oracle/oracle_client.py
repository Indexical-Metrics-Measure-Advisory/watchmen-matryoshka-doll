import json
from typing import List

import cx_Oracle
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from watchmen.common.utils.date_utils import DateTimeEncoder
from watchmen.config.config import settings
from watchmen.database.datasource.data_source import DataSource, DataSourceParam

SID = "SID"


class OracleEngine(object):
    engine = None

    def dumps(self, o):
        return json.dumps(o, cls=DateTimeEncoder)

    def find_sid(self, params: List[DataSourceParam]):
        for param in params:
            if param.name == SID:
                return param.value

    def __init__(self, database: DataSource):

        cx_Oracle.init_oracle_client(lib_dir=settings.ORACLE_LIB_DIR)

        sid = self.find_sid(database.params)
        if sid:
            dsn = cx_Oracle.makedsn(database.host,
                                    database.port, sid=sid)

        if sid is None and database.name is not None:
            dsn = cx_Oracle.makedsn(database.host,
                                    database.port, service_name=database.name)

        pool = cx_Oracle.SessionPool(
            database.username, database.password, dsn=dsn,
            min=10, max=10, increment=0, threaded=True, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT
        )

        # engine = create_engine(connection_url, future=True)
        self.engine = create_engine("oracle+cx_oracle://", creator=pool.acquire,
                                    poolclass=NullPool, coerce_to_decimal=False, echo=False, optimize_limits=True)

    def get_engine(self):
        return self.engine
