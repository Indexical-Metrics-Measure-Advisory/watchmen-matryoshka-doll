from watchmen.connector.local_connector import row_data_load
from watchmen.space.factors.factor import Factor, FactorType
from watchmen.pipeline.pipeline import basic_schema, update_schema
from watchmen.row_data import Domain
from watchmen.storage.factor_storage import save_factor








def test_basic_schema():
    json = row_data_load('../assert/data/policy.json')
    id = basic_schema(json, Domain.INSURANCE)
    print(id)
    assert id is not None


def suggestions_match_rule_for_master_topics():
    pass


# mapping to exist domain model
def test_confirm_schema():
    json = row_data_load('../assert/data/policy.json')
    id = basic_schema(json, Domain.INSURANCE)
    result = update_schema(id, json, Domain.INSURANCE)
    assert result is not None


# def test_import_instance_data():
#     pickle_data = pickle.dumps(row_data_load('../../test/data/instance_data.json'))
#     model_schema_set = ModelSchemaSet.parse_raw(
#         pickle_data, content_type='application/pickle', allow_pickle=True
#     )
#     json = row_data_load('../../test/data/policy.json')
#     result = import_data(json, model_schema_set)
#     assert result is not None


def test_save_factor():
    factor = Factor()
    factor.type = FactorType.AtomicIndex
    factor.value = "field name"
    factor.topicId = "master_topic_id "
    # factor.groupId
    # print(factor.dict())
    result = save_factor(factor.dict())
    assert result.inserted_id is not None


def run_factors():
    pass


def generate_standard_report_suggest():
    pass


def import_uw_rule():
    pass


def generate_report():
    pass


def create_new_factor():
    pass


def create_pipeline():
    pass
