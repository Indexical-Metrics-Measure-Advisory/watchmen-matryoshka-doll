# import prestodb
import trino

from watchmen.config.config import settings

conn = trino.dbapi.connect(
    host=settings.PRESTO_HOST,
    port=settings.PRESTO_PORT,
    user=settings.PRESTO_USER,
    catalog=settings.PRESTO_CATALOG,
    schema=settings.PRESTO_SCHEMA,
)


def get_connection():
    return conn
