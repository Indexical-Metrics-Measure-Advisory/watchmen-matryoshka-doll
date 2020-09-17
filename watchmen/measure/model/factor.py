from pydantic import BaseModel


class Factor(BaseModel):
    factorId: str = None
    value: object = None,
    name: str = None,
    isQuantify: bool = None,
    isResult: bool = None
    layerId: str = None
    sceneId: str = None
    isDerivedIndex: bool = None
    timePeriodId: str = None
    isAtomicIndex: bool = None
    isDimension: bool = None
    fromDimensionId: str = None
    isTransactionalIndicators: bool = None,
    isStockIndex: bool = None,
    isDerivativeIndicators: bool = None



