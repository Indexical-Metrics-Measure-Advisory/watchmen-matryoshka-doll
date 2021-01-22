from datetime import datetime

from pypika import Query, Table

import prestodb

from watchmen.common.pagination import Pagination
from watchmen.monitor.presto.index import load_query_status
from watchmen.report.engine.dataset_engine import load_dataset_by_subject_id, \
     load_chart_dataset


from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN

client = get_client(WATCHMEN)

collection_list_name = client.list_collection_names()

client.get_collection("_schema")



def test_load_presto():
    print(load_query_status())


def test_list_collection():
    print(collection_list_name)

    data =client.get_collection("_schema")

    print(data.find_one())




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

    s1 ="SELECT topic_gi_policy.beforeVatPremium,topic_gi_policy.agentCode,topic_gi_risk.vehicleModel FROM topic_gi_policy JOIN topic_gi_risk ON topic_gi_risk.policyId=topic_gi_policy.policyId "
    s2 = "SELECT count(*) FROM topic_gi_policy"
    s3 = "SELECT topic_gi_customer.city FROM topic_gi_customer"
    s4 = "SELECT * FROM topic_gi_risk"
    t =Table('topic_gi_policy')
    q = Query.from_(t).select(t['orgCode'])
    print(s1)
    cur.execute(s2)
    rows = cur.fetchall()

    print(rows)


def test_sql_generator():





    print(q.get_sql())




def test_sql_generator_subject():
    pagination = Pagination(pageSize=100,pageNumber=1)
    load_dataset_by_subject_id("801785069239795712",pagination)


def test_sql_generator_chart():
    data = load_chart_dataset("800799662100447232","4789f568-776a-4d06-833f-2e051606bda1")

    print(data)



def test_datetime():

    date =datetime.fromisoformat("2021-12-12")

    print(date.weekday())
    pass