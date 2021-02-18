import logging

log = logging.getLogger("app." + __name__)


def init_system_topics():
    pass


def init_pipeline_monitor():
    pass


def init_stage_monitor():
    pass


def __check_init_status():
    # TODO check db record
    return False


def init_monitor_metadata():
    if __check_init_status():
        log.info("system already initialized")
    else:
        init_system_topics()
        init_pipeline_monitor()
        init_stage_monitor()
        log.info("system successfully initialized")
