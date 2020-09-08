
from pydantic import BaseModel
from typing import Optional


class Context(BaseModel):
    name: str
    description: Optional[str] = None
    context_code: str
    context_type: str




