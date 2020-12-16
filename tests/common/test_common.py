from watchmen.common.mongo.index import check_collection_if_exist


def test_check_collection_name():

    flag = check_collection_if_exist(None,"topic_policy")

    assert flag is True