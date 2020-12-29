import json

from watchmen.raw_data_back.rule_context import RuleContext
from watchmen.raw_data_back.rule_schema import RuleType
from watchmen.common.rule.import_rule import import_single_rule


# TODO[next] add raw_data_back in parameter


def test_import_rule():
    rule = "if the customer’s gender is male and the age is over 60 and the main clause limit exceeds 100W, " \
           "then the underwriting level is set to advanced."

    rule2 = "if the premium is greater than 2000, then the underwriting level is 2."

    rule_context = RuleContext()
    rule_context.ruleName = "test_rule_1"
    rule_context.type = RuleType.natural_language
    result = import_single_rule(rule_context, rule2)
    print(json.dumps(result))
    result = import_single_rule(rule_context, rule)
    print(json.dumps(result))


