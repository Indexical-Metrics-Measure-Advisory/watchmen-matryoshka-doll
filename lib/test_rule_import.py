from lib.model.rule_context import RuleContext
from lib.model.rule_schema import RuleType
from lib.service.import_rule import import_single_rule

import json


# TODO add schema in parameter

rule = "if the customer’s gender is male and the age is over 60 and the main clause limit exceeds 100W, " \
       "then the underwriting level is set to advanced."


rule2 = "if the premium is greater than 2000, then the underwriting level is 2."

rule_context = RuleContext()
rule_context.ruleName="test_rule_1"
rule_context.type = RuleType.natural_language

result = import_single_rule(rule_context,rule2)
print(json.dumps(result))

result = import_single_rule(rule_context,rule)

print(json.dumps(result))



