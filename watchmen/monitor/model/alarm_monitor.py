from watchmen.common.mongo_model import MongoModel
from watchmen.monitor.model.pipeline_monitor import ConditionHolder, FromTopicHolder


class AlarmMonitor(MongoModel,ConditionHolder,FromTopicHolder):
    pass
