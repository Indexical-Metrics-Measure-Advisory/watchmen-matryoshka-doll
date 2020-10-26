
import yaml
import os

TEMPLATE_YAML = "/insurance_template.yaml"


def load_template():
    current_path = os.path.abspath(os.path.dirname(__file__))
    # TODO merge template
    print(current_path)
    with open(current_path + TEMPLATE_YAML, 'r') as stream:
        try:
            template = yaml.safe_load(stream)
            return template
        except yaml.YAMLError as exc:
            print(exc)


