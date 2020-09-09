import json

from watchmen.schema.generate.model_schema_generater import generate_basic_schema
from watchmen.schema.model_schema import Domain


def generate_schema(key: str, data: json, domain: Domain):

    return generate_basic_schema(key, data, domain)