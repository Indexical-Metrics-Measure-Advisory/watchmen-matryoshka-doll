from typing import List

from watchmen.common.mongo_model import MongoModel
from watchmen.pipeline.model.pipeline import Pipeline


class PipelineFlow(MongoModel):
    topicId: str = None
    consume: List[Pipeline]
    produce: List[Pipeline]
