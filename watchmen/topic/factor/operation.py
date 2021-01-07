from typing import List

from pydantic import BaseModel


class Operation(BaseModel):
    operateId = str = None
    factorIds = List[str] = None
    formula = str = None
    type = str = None
