from pypika import Query, Table

from watchmen.common.mongo.index import check_collection_if_exist
import prestodb

from watchmen.report.engine.dataset_engine import load_dataset_by_subject_id, \
     load_chart_dataset


def test_presto_connection():

    conn = prestodb.dbapi.connect(
        host='localhost',
        port=8080,
        user='the-user',
        catalog='mongo',
        schema='watchmen',
    )
    cur = conn.cursor()
    # t = Table("topic_policy")
    # t2 = Table("topic_raw_policy")
    # q = Query.from_(t).select(t["premium"])

    # print(q.get_sql())
    cur.execute("select sum(premium) from topic_policy group by number")
    rows = cur.fetchall()

    print(rows)


def test_sql_generator():





    q = Query.from_('topic_customers').select('name')


    print(q.get_sql())




def test_sql_generator_subject():
   load_dataset_by_subject_id("800799662100447232")


def test_sql_generator_chart():
    data = load_chart_dataset("800799662100447232","4789f568-776a-4d06-833f-2e051606bda1")

    print(data)