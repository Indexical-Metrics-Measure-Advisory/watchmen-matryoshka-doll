
def get_primary_key(table_name):
    if table_name == 'topics':
        return 'topicId'
    elif table_name == 'console_space_subjects':
        return 'subjectId'
    elif table_name == 'pipelines':
        return 'pipelineId'
    elif table_name == 'users':
        return 'userId'
    elif table_name == 'console_dashboards':
        return 'dashboardId'
    elif table_name == 'pipeline_graph':
        return 'pipelineGraphId'
    elif table_name == 'console_spaces':
        return 'connectId'
    elif table_name == 'console_space_favorites':
        return 'userId'
    elif table_name == 'spaces':
        return 'spaceId'
    elif table_name == 'console_space_subjects':
        return 'subjectId'
    elif table_name == 'console_reports':
        return 'reportId'
    elif table_name == 'user_groups':
        return 'userGroupId'
    elif table_name == 'enums':
        return 'enumId'
    elif table_name == 'console_reports':
        return 'reportid'
    elif table_name == "console_space_last_snapshot":
        return  "userid"
