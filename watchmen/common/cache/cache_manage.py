from cacheout import CacheManager, Cache

TOPIC_BY_NAME = "topic_by_name"
TOPIC_BY_ID = "topic_by_id"
PIPELINE_BY_ID = "pipeline_by_id"
PIPELINES_BY_TOPIC_ID = "pipelines_by_topic_id"
COLUMNS_BY_TABLE_NAME = "columns_by_table_name"

class WatchmenCache(Cache):
    pass


cacheman = CacheManager({
    TOPIC_BY_NAME: {"maxsize": 300, "ttl": 0, "default": None},
    TOPIC_BY_ID: {"maxsize": 300, "ttl": 0, "default": None},
    PIPELINE_BY_ID: {"maxsize": 200, "ttl": 0, "default": None},
    PIPELINES_BY_TOPIC_ID: {"maxsize": 200, "ttl": 0, "default": None},
    COLUMNS_BY_TABLE_NAME: {"maxsize": 200, "ttl": 0, "default": None}
},
    WatchmenCache)