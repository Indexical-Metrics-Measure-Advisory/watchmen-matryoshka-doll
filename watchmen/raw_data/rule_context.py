from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel
from watchmen.raw_data.rule_schema import RuleType, DSLType


class RuleContext(MongoModel):
    type: RuleType = None
    dsl: DSLType = None
    orgId: int = None
    orgName: str = None
    productId: int = None
    productName: str = None
    ruleId: int = None
    ruleName: str = None
