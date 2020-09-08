from lib.model.generate.rule_schema_generater import generate_schema_rules
from lib.model.rule_context import RuleContext


def import_single_rule(rule_context: RuleContext, rule: str):
    print(rule)

    # TODO check rule context data

    return generate_schema_rules(rule_context, rule)


def import_rule_result():
    pass
