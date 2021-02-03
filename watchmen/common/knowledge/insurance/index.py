import os

import yaml
from watchmen.space.factors.factor import Factor
from watchmen.space.factors.topic import Topic

TEMPLATE_YAML = "/insurance_template.yml"


def load_template():
    current_path = os.path.abspath(os.path.dirname(__file__))
    # TODO merge template
    # print(current_path)
    with open(current_path + TEMPLATE_YAML, 'r') as stream:
        try:
            templates = yaml.safe_load(stream)["topic_list"]
            topic_list = []
            # print(templates)
            for template in templates:
                # topic.topic_name = template.keys()
                for key, value in template.items():
                    topic = Topic()
                    topic.businessKey = "insurance_template"
                    # for x in template.values():
                    topic.topicName = key
                    for factor_name, factor_details in value.items():
                        factor = Factor(**factor_details)
                        factor.factorName = factor_name
                        factor.topicName = key
                        topic.factors.append(factor)
                    topic_list.append(topic)
            # print(topic_list)
            return topic_list
        except yaml.YAMLError as exc:
            print(exc)

# def load_template_from_db():
#     current_path = os.path.abspath(os.path.dirname(__file__))
#     # TODO merge template
#     print(current_path)
#     with open(current_path + TEMPLATE_YAML, 'r') as stream:
#         try:
#             template = yaml.safe_load(stream)
#             return template
#         except yaml.YAMLError as exc:
#             print(exc)
