from pypika import Query

from watchmen.common.mongo.index import check_collection_if_exist
import prestodb

def test_presto_connection():

    conn = prestodb.dbapi.connect(
        host='localhost',
        port=8080,
        user='the-user',
        catalog='mongo',
        schema='watchmen',
    )
    cur = conn.cursor()
    q = Query.from_('topic_customers').select('name')
    cur.execute(q.get_sql())
    rows = cur.fetchall()

    print(rows)


def test_sql_generator():
    q = Query.from_('topic_customers').select('name')


    print(q.get_sql())

