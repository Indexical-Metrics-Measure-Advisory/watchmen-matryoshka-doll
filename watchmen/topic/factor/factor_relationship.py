from pydantic import BaseModel


class FactorRelationship(BaseModel):
    relationshipId: str = None
