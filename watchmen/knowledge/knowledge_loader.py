import json

from watchmen.row_data.model_schema import Domain

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


def __check_domain(domain):
    return True


def find_template_by_domain(domain):
    # check domain name
    if __check_domain(domain):
        topic_list = dynamic_import_template(domain)
        return topic_list


def dynamic_import_template(name):
    name = "watchmen.knowledge."+name + ".index"
    template = __import__(name, fromlist=[''])
    return template.load_template()
