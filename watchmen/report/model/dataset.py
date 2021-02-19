from typing import List, Dict

from pydantic import BaseModel

from watchmen.report.model.column import Column


class Dataset(BaseModel):
    columns: List[Column] = None
    results: Dict = {}
