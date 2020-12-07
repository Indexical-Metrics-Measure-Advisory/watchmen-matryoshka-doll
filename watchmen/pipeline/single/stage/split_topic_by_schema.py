# import dask


def init(**kwargs):
    # if schema is empty ,generate a row schema
    # split data base on schema
    # return topic_list , relationship and schema
    row_schema = kwargs["row_schema_name"]

    def run(data):
        print(row_schema)
        print(data)
        return {"topic_a": "a", "topic_B": "b"}

    return run


def trigger(**kwargs) -> bool:

    pass
