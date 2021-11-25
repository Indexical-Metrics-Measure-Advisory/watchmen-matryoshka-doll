from model.model.common.watchmen_model import WatchmenModel

from watchmen.raw_data.rule_schema import RuleType, DSLType


class RuleContext(WatchmenModel):
    type: RuleType = None
    dsl: DSLType = None
    orgId: int = None
    orgName: str = None
    productId: int = None
    productName: str = None
    ruleId: int = None
    ruleName: str = None
