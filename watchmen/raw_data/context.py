from typing import Optional

from pydantic import BaseModel


class Context(BaseModel):
    name: str
    description: Optional[str] = None
    context_code: str
    context_type: str
