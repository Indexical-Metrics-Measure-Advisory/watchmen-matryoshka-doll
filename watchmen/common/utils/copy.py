from typing import Dict

from watchmen.raw_data.model_field import ModelField
from watchmen.raw_data.model_schema import ModelSchema
from model.model.topic.factor import Factor
from model.model.topic.topic import Topic


def convert_business_fields_to_factors(business_fields_dict: Dict[str, ModelField]):
    factors = []
    for key, businessField in business_fields_dict.items():
        factor = Factor()
        factor.factorName = businessField.name
        factor.type = businessField.type
        factors.append(factor)

    return factors


def direct_copy_raw_schema_to_topic(model_schema: ModelSchema, topic: Topic):
    if topic is None:
        topic = Topic()
    topic.topicName = model_schema.name
    topic.factors = convert_business_fields_to_factors(model_schema.businessFields)
    return topic
