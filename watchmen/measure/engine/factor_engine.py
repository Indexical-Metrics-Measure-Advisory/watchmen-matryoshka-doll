from watchmen.measure.model.factor import Factor, FactorType


def run_factors_on_topic_data(factors:List[Factor] ,topic_data):
    #





    pass


def _get_value_from_topic(value, data):

    # return value
    pass


def _execute_factor_on_topic_data(factor:Factor,topic_data):

    if factor.type is FactorType.AtomicIndex:
        value = _get_value_from_topic(factor.value,topic_data)

    if factor.type is FactorType.DerivedIndex:

        # load time period aggregate table
        # calculate value base on dependency factor
        # save data back to table
        pass

    if factor.type is FactorType.DerivativeIndicators:
        pass


    # return topic data with factor value


    pass




