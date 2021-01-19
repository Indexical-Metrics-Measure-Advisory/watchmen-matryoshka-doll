import prestodb

conn = prestodb.dbapi.connect(
    host='localhost',
    port=8080,
    user='the-user',
    catalog='mongo',
    schema='watchmen',
)


def get_connection():
    return conn
