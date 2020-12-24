from pypika import Table,Query


TOPIC_PREFIX ="topic_"


def generate_sql(topic_name,factors,filter):
    topic = Table(TOPIC_PREFIX+topic_name)
    return Query.from_(topic).select(*factors)

