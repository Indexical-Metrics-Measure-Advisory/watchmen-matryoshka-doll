from enum import Enum

from watchmen.common.mongo_model import MongoModel


class FactorType(Enum):
    SEQUENCE = "sequence",
    NUMBER = "number",
    TEXT = "text",
    DATETIME = "datetime",
    BOOLEAN = "boolean",
    ENUM = "enum",
    OBJECT = "object",
    ARRAY = "array",


class Factor(MongoModel):
    type: str = None
    factorId: str = None
    name: str = None
    label: str = None
    description: str = None


'''
    factor_id: int = None

    factor_name:str = None

    value: str = None

    alias: List[str] = None

    topicId: str = None

    valueType: str = None

    topicName:str = None
    # isQuantify: bool = None,
    # isResult: bool = None
    groupId: str = None

    type: FactorType = None

    isDimension: bool = None

    isMeasure: bool = None

    timePeriod: str = None

    # factorDimension: FactorDimension = None
    isTransactionalIndicators: bool = True

    isStockIndex: bool = False

    isCompoundIndex:bool = False

    isWordFrequency: bool = False

    codeTable: str = None

    isTag: bool = False
'''
