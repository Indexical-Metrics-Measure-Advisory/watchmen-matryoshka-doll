from pydantic import BaseModel

from watchmen.row_data.rule_schema import RuleType, DSLType


class RuleContext(BaseModel):
    type: RuleType = None
    dsl: DSLType = None
    orgId: int = None
    orgName: str = None
    productId: int = None
    productName: str = None
    ruleId:int = None
    ruleName: str = None
