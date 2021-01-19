from pypika import Query, Table

from watchmen.common.presto.presto_client import get_connection
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def build_columns(columns):
    topic_dict = {}

    for column in columns:
        topic = get_topic_by_id(column.topicId)

        key = build_collection_name(topic.name)
        if key in topic_dict:
            factor = get_factor(column.factorId, topic)
            topic_dict[key].append(factor.name)
        else:
            topic_dict[key] = []
            factor = get_factor(column.factorId, topic)
            topic_dict[key].append(factor.name)

    q = Query._builder()
    for key, items in topic_dict.items():
        t = Table(key)
        q = q.from_(Table(key))
        for item in items:
            q = q.select(t[item])

    return q


def load_dataset_by_subject_id(subject_id):
    console_subject = load_console_subject_by_id(subject_id)
    dataset = console_subject.dataset
    # query =None
    if dataset is not None:
        # build columns
        if len(dataset.columns) > 0:
            query = build_columns(dataset.columns)

    conn = get_connection()
    print(query.get_sql())
    cur = conn.cursor()
    cur.execute(query.get_sql())
    rows = cur.fetchall()
    print(rows)
    return rows
