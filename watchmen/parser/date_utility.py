from pypika import CustomFunction
from pypika.terms import PseudoColumn

from watchmen.parser.constants import Unit


def date_diff(unit: Unit, arg1: CustomFunction, arg2: CustomFunction) -> CustomFunction:
    func_date_diff = CustomFunction("DATE_DIFF", ["col1", "col2", "col3"])
    return func_date_diff(unit, arg1, arg2)


def current_date() -> PseudoColumn:
    return PseudoColumn('current_date')



