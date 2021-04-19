import json

from sqlalchemy import create_engine

from watchmen.common.utils.date_utils import DateTimeEncoder
from watchmen.config.config import settings
import cx_Oracle


def dumps(o):
    return json.dumps(o, cls=DateTimeEncoder)


cx_Oracle.init_oracle_client(lib_dir=settings.ORACLE_LIB_DIR)

connection_url = "oracle+cx_oracle://%s:%s@%s:%s/?" \
                 "service_name=%s&encoding=UTF-8&nencoding=UTF-8" % (settings.ORACLE_USER,
                                                                     settings.ORACLE_PASSWORD,
                                                                     settings.ORACLE_HOST,
                                                                     settings.ORACLE_PORT,
                                                                     settings.ORACLE_SERVICE)

engine = create_engine(connection_url, future=True)
