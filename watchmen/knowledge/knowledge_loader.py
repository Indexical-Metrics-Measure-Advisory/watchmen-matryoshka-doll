import json

from watchmen.lake.model_schema import Domain

domain_conf = {
    "insurance_en": "./data/lexicon/insurance-data.json"
}


def load_lexicon(domain: str, language: str):
    with open(find_lexicon_path(domain, language)) as json_file:
        return json.load(json_file)


def find_lexicon_path(domain: str, language: str):
    if domain is not None:
        key = domain + "_" + language
    else:
        key = Domain.INSURANCE + "_" + language

    return domain_conf[key]







