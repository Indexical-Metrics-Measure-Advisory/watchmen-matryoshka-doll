from typing import List

from watchmen.common.watchmen_model import WatchmenModel


class Space(WatchmenModel):
    spaceId: str = None
    topicIds: List[str] = None
    groupIds: List[str] = None
    name: str = None
    description: str = None
