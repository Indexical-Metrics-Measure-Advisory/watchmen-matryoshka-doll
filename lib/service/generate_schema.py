import json

from lib.model.generate.model_schema_generater import generate_basic_schema
from lib.model.model_schema import Domain


def generate_schema(key: str, data: json, domain: Domain):
    generate_basic_schema(key, data, domain)