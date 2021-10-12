from enum import Enum

from watchmen.common.watchmen_model import WatchmenModel


class FactorType(Enum):
    SEQUENCE = "sequence"
    NUMBER = "number"
    TEXT = "text"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    ENUM = "enum"
    OBJECT = "object"
    ARRAY = "array"


# class FactorEncryptMethod(Enum):
#     NONE = 'none',
#     AES256_PKCS5_PADDING = 'AES256-PKCS5-PADDING',
#     MD5 = 'MD5',
#     SHA256 = 'SHA256',
#     MASK_MAIL = 'MASK-MAIL',
#     MASK_CENTER_3 = 'MASK-CENTER-3',
#     MASK_CENTER_5 = 'MASK-CENTER-5',
#     MASK_LAST_3 = 'MASK-LAST-3',
#     MASK_LAST_6 = 'MASK-LAST-6',
#     MASK_DAY = 'MASK-DAY',
#     MASK_MONTH = 'MASK-MONTH',
#     MASK_MONTH_DAY = 'MASK-MONTH-DAY'


class Factor(WatchmenModel):
    type: str = None
    factorId: str = None
    name: str = None
    enumId: str = None
    label: str = None
    description: str = None
    defaultValue: str = None
    flatten: bool = None
    indexGroup: str = None
    tenantId: str = None
    encrypt: str = None


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
