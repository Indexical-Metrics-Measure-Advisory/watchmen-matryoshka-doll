import json

import cx_Oracle
from sqlalchemy import create_engine

from watchmen.common.utils.date_utils import DateTimeEncoder
from watchmen.config.config import settings
from sqlalchemy.pool import NullPool


def dumps(o):
    return json.dumps(o, cls=DateTimeEncoder)


cx_Oracle.init_oracle_client(lib_dir=settings.ORACLE_LIB_DIR)

connection_url = "oracle+cx_oracle://%s:%s@%s:%s/?" \
                 "service_name=%s&encoding=UTF-8&nencoding=UTF-8" % (settings.ORACLE_USER,
                                                                     settings.ORACLE_PASSWORD,
                                                                     settings.ORACLE_HOST,
                                                                     settings.ORACLE_PORT,
                                                                     settings.ORACLE_SERVICE)

dsn = cx_Oracle.makedsn(settings.ORACLE_HOST, settings.ORACLE_PORT, service_name=settings.ORACLE_SERVICE)

pool = cx_Oracle.SessionPool(
    settings.ORACLE_USER, settings.ORACLE_PASSWORD, connection_url,
    min=2, max=5, increment=1, threaded=True
)

# engine = create_engine(connection_url, future=True)
engine = create_engine("oracle+cx_oracle://", creator=pool.acquire, poolclass=NullPool)