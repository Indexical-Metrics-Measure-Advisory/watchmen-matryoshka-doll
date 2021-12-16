class TableDefinition(object):

    def get_primary_key(self, table_name):
        return self.get_pid(table_name)
        # return pid

    def get_pid(self, table_name):
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
            return 'reportId'
        elif table_name == "console_space_last_snapshot":
            return "userId"
        elif table_name == "tenants":
            return "tenantId"
        elif table_name == "pats":
            return "patId"
        elif table_name == "data_sources":
            return "dataSourceId"
        elif table_name == "external_writer":
            return "writerId"
        elif table_name == "factor_index":
            return "factorindexid"
        else:
            raise Exception("table_name does not exist {0}".format(table_name))
