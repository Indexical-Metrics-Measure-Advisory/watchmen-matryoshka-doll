class TableDefinition(object):

    def get_primary_key(self, table_name):
        pid = self.get_pid(table_name)
        return pid

    def get_pid(self, table_name):
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
        elif table_name == "pats":
            pid = "patId"
        elif table_name == "data_sources":
            pid = "dataSourceId"
        elif table_name == "external_writer":
            pid = "writerId"
        elif table_name == "factor_index":
            pid = "factorindexid"
        return pid
