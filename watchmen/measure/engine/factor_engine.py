from typing import List

from watchmen.measure.model.factor import Factor, FactorType


class DependencyProvider(object):
    def find_related_topic(self):
        pass


def run_factors_on_topic_data(factors:List[Factor] ,topic_data,dependency_provider:DependencyProvider):
    if dependency_provider is None:
        dependency_provider = DependencyProvider()

    for factor in factors:
       result =  __execute_factor_on_topic_data(factor,topic_data,dependency_provider)
       # update_topic_data #TODO audit

    pass


def __get_value_from_topic(value, data):
    return data[value]


def __execute_factor_on_topic_data(factor:Factor,topic_data,dependency_provider):

    if factor.type is FactorType.AtomicIndex:
        value = __get_value_from_topic(factor.value,topic_data)

    if factor.type is FactorType.DerivedIndex:

        # load time period aggregate table
        # calculate value base on dependency factor
        # save data back to table
        pass

    if factor.type is FactorType.DerivativeIndicators:
        pass


    # return topic data with factor value

    return {}




