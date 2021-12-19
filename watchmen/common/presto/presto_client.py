from watchmen_boot.config.config import settings

PRESTODB = "prestodb"
TRINO = "trino"

if settings.PRESTO_ON and settings.PRESTO_LIB == TRINO:
    import trino

    conn = trino.dbapi.connect(
        host=settings.PRESTO_HOST,
        port=settings.PRESTO_PORT,
        user=settings.PRESTO_USER,
        # catalog=settings.PRESTO_CATALOG,
        # schema=settings.PRESTO_SCHEMA,
    )
elif settings.PRESTO_ON and settings.PRESTO_LIB == PRESTODB:
    import prestodb

    conn = prestodb.dbapi.connect(
        host=settings.PRESTO_HOST,
        port=settings.PRESTO_PORT,
        user=settings.PRESTO_USER,
        # catalog=settings.PRESTO_CATALOG,
        # schema=settings.PRESTO_SCHEMA,
    )
else:
    conn = {}


def get_connection():
    return conn
