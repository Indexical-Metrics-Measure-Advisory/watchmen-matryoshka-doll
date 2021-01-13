from watchmen.pipeline.index import trigger_topic


def topic_event_trigger(func):
    def wrapper_after(*args, **kwargs):
        func(*args, **kwargs)
        trigger_topic(*args, **kwargs)
    return wrapper_after



