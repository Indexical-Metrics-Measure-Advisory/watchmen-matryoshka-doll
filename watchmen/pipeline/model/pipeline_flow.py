from typing import List

from watchmen.common.watchmen_model import WatchmenModel
from watchmen.pipeline.model.pipeline import Pipeline


class PipelineFlow(WatchmenModel):
    topicId: str = None
    consume: List[Pipeline]
    produce: List[Pipeline]
    tenantId: str = None
