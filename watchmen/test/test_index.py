from watchmen.connector.local_connector import row_data_load
from watchmen.index import select_domain, import_data
from watchmen.storage.lake_data_storage import batch_import_data


def test_select_domain():
    master_space  = select_domain("insurance")

    assert master_space is not None


def test_import_instance_data():
    # data =
    # # data2 = row_data_load('../../test/data/policy.json')
    import_data([row_data_load('../../test/data/policy.json'),row_data_load('../../test/data/policy.json')],"policy")




