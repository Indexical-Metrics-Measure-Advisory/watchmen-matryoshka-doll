from pydantic import BaseModel


class Topic(BaseModel):
    topic_id: int
    name: str
    topic_type: str

    '''
    topic_id: str = None

    topic_name: str = None

    businessKey  : str = None

    factors: List[Factor] = []

    alias: List[str] = None

    indexKey : List[str] = None

    isUnification:bool = False

    embeddedRelationship: List[str] = None

    parentTopicId: str = None
    '''
