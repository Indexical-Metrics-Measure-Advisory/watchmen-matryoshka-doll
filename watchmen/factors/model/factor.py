from enum import Enum
from typing import List

from pydantic import BaseModel


class FactorType(str, Enum):
    AtomicIndex = "AtomicIndex"
    DerivedIndex = "DerivedIndex"
    DerivativeIndicators = "DerivativeIndicators"


class Factor(BaseModel):

    factorId: int = None

    factor_name:str = None

    value: str = None

    alias: List[str] = None

    topicId: str = None
    # isQuantify: bool = None,
    # isResult: bool = None
    groupId: str = None

    type: FactorType = None

    # isDimension: bool = None

    timePeriodId: str = None

    # factorDimension: FactorDimension = None
    isTransactionalIndicators: bool = None

    isStockIndex: bool = False

    isWordFrequency: bool = False

    codeTable: str = None

    isTag: bool = False



