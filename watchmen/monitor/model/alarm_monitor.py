from model.model.common.watchmen_model import WatchmenModel
from watchmen.monitor.model.pipeline_monitor import ConditionHolder, FromTopicHolder


class AlarmMonitor(WatchmenModel, ConditionHolder, FromTopicHolder):
    pass
