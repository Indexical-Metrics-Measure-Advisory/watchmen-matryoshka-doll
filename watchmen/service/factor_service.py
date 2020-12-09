from watchmen.space.factors.engine.factor_engine import run_factors_on_topic_data
from watchmen.space.storage.factor_storage import load_factors_by_topic_id


def __find_root_entity(entity_set):
    return entity_set[0]
    # pass


def run_factors(entity_set):
    root= __find_root_entity (entity_set)
    factors = load_factors_by_topic_id(root.topic_id)

    # find dependency topic for factors

    run_factors_on_topic_data(factors,root)

    ## run factors for each topic

    ## save factors result to topic collection

    # trace issue factor





    # find match factor



    pass