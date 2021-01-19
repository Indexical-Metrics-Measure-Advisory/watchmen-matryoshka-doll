from pypika import Query, Table

from watchmen.common.mongo.index import check_collection_if_exist
import prestodb

from watchmen.report.engine.dataset_engine import load_dataset_by_subject_id


def test_presto_connection():

    conn = prestodb.dbapi.connect(
        host='localhost',
        port=8080,
        user='the-user',
        catalog='mongo',
        schema='watchmen',
    )
    cur = conn.cursor()
    t = Table("topic_policy")
    t2 = Table("topic_raw_policy")
    q = Query.from_(t).select(t["premium"])

    print(q.get_sql())
    cur.execute(q.get_sql())
    rows = cur.fetchall()

    print(rows)


def test_sql_generator():





    q = Query.from_('topic_customers').select('name')


    print(q.get_sql())




def test_sql_generator_subject():
   load_dataset_by_subject_id("800854285611958272")
