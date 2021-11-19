import json

from watchmen.common.utils.date_utils import DateTimeEncoder


def dumps(o):
    return json.dumps(o, cls=DateTimeEncoder)


"""
cx_Oracle.init_oracle_client(lib_dir=settings.ORACLE_LIB_DIR)

if settings.ORACLE_SID != "":
    dsn = cx_Oracle.makedsn(settings.ORACLE_HOST,
                            settings.ORACLE_PORT, sid=settings.ORACLE_SID)

if settings.ORACLE_SID == "" and settings.ORACLE_SERVICE != "":
    dsn = cx_Oracle.makedsn(settings.ORACLE_HOST,
                            settings.ORACLE_PORT, service_name=settings.ORACLE_SERVICE)

pool = cx_Oracle.SessionPool(
    settings.ORACLE_USER, settings.ORACLE_PASSWORD, dsn=dsn,
    min=10, max=10, increment=0, threaded=True, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT
)

engine = create_engine("oracle+cx_oracle://", creator=pool.acquire,
                       poolclass=NullPool, coerce_to_decimal=False, echo=False, optimize_limits=True)
"""
