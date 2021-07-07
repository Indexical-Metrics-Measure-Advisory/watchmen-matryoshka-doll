## TODO  factor it

from cacheout import Cache

from watchmen.config.config import settings, PROD

cache = Cache()


def get_primary_key(table_name):
    if table_name in cache and settings.ENVIRONMENT == PROD:
        return cache.get(table_name)

    pid = get_pid(table_name)
    cache.set(table_name, pid)
    return pid


def get_pid(table_name):
    if table_name == 'topics':
        pid = 'topicId'
    elif table_name == 'console_space_subjects':
        pid = 'subjectId'
    elif table_name == 'pipelines':
        pid = 'pipelineId'
    elif table_name == 'users':
        pid = 'userId'
    elif table_name == 'console_dashboards':
        pid = 'dashboardId'
    elif table_name == 'pipeline_graph':
        pid = 'pipelineGraphId'
    elif table_name == 'console_spaces':
        pid = 'connectId'
    elif table_name == 'console_space_favorites':
        pid = 'userId'
    elif table_name == 'spaces':
        pid = 'spaceId'
    elif table_name == 'console_space_subjects':
        pid = 'subjectId'
    elif table_name == 'console_reports':
        pid = 'reportId'
    elif table_name == 'user_groups':
        pid = 'userGroupId'
    elif table_name == 'enums':
        pid = 'enumId'
    elif table_name == 'console_reports':
        pid = 'reportId'
    elif table_name == "console_space_last_snapshot":
        pid = "userId"
    elif table_name == "tenants":
        pid = "tenantId"
    return pid
