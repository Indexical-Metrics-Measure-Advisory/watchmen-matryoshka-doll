from typing import List

from pydantic import BaseModel

from watchmen.measure.model.factor_dimension import FactorDimension
from watchmen.measure.model.factor_layer import FactorLayer
from watchmen.measure.model.factor_time_period import FactorTimePeriod
from watchmen.measure.model.scene import Scene


class Factor(BaseModel):
    factorId: str = None
    value: object = None,
    name: str = None,
    isQuantify: bool = None,
    isResult: bool = None
    layer: FactorLayer = None
    scene: Scene = None
    isDerivedIndex: bool = None
    timePeriod: FactorTimePeriod = None
    isAtomicIndex: bool = None
    isDimension: bool = None
    factorDimension: FactorDimension = None
    isTransactionalIndicators: bool = None,
    isStockIndex: bool = None,
    isDerivativeIndicators: bool = None
    fieldIds: List[str] = None




