from pydantic import BaseModel


class Topic(BaseModel):
    topicId: int=None
    name: str=None
    type: str=None
    factors: list =[]
    # alias: List[str] = None
    is_aggregate: bool = False
    businessKey: list = []

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
