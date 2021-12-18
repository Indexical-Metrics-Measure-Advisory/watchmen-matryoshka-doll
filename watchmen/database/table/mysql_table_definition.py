from sqlalchemy import MetaData, Table, Column, String, Date, DateTime, Integer, JSON, Boolean

from watchmen_boot.config.config import settings
from watchmen_boot.utils.singleton import singleton
from watchmen.database.table.base_table_definition import TableDefinition


@singleton
class MysqlTableDefinition(TableDefinition):

    def __init__(self):
        self.metadata = MetaData()

        self.users_table = Table("users", self.metadata,
                                 Column('userid', String(60), primary_key=True),
                                 Column('name', String(45), nullable=False),
                                 Column('nickname', String(45), nullable=True),
                                 Column('password', String(100), nullable=True),
                                 Column('is_active', String(5), nullable=True),
                                 Column('groupids', JSON, nullable=True),
                                 Column('role', String(45), nullable=True),
                                 Column('createtime', String(50), nullable=True),
                                 Column('tenantid', String(60), nullable=False),
                                 Column('lastmodified', Date, nullable=True)
                                 )

        self.tenants_table = Table("tenants", self.metadata,
                                   Column('tenantid', String(60), primary_key=True),
                                   Column('name', String(45), nullable=False),
                                   Column('createtime', String(50), nullable=True),
                                   Column('lastmodified', Date, nullable=True)
                                   )

        self.external_writer = Table("external_writer", self.metadata,
                                     Column('writerid', String(50), primary_key=True),
                                     Column('writercode', String(50), nullable=False),
                                     Column('type', String(50), nullable=False),
                                     Column('pat', String(50), nullable=False),
                                     Column('url', String(50), nullable=False),
                                     Column('tenantid', String(60), nullable=True),
                                     Column('createtime', String(50), nullable=True),
                                     Column('lastmodified', Date, nullable=True)
                                     )

        self.user_groups_table = Table("user_groups", self.metadata,
                                       Column('usergroupid', String(60), primary_key=True),
                                       Column('name', String(45), nullable=False),
                                       Column('description', String(45), nullable=True),
                                       Column('userids', JSON, nullable=True),
                                       Column('spaceids', JSON, nullable=True),
                                       Column('createtime', String(50), nullable=True),
                                       Column('tenantid', String(60), nullable=True),
                                       Column('lastmodified', Date, nullable=True)
                                       )

        self.console_space_last_snapshot_table = Table("console_space_last_snapshot", self.metadata,
                                                       Column('userid', String(60), primary_key=True),
                                                       Column('language', String(5), nullable=True),
                                                       Column('lastdashboardid', String(25), nullable=True),
                                                       Column('admindashboardid', String(25), nullable=True),
                                                       Column('favoritepin', String(5), nullable=True),
                                                       Column('tenantid', String(60), nullable=False),
                                                       Column('createtime', String(50), nullable=True),
                                                       Column('lastmodified', Date, nullable=True)
                                                       )

        self.console_dashboards_table = Table("console_dashboards", self.metadata,
                                              Column('dashboardid', String(60), primary_key=True),
                                              Column('name', String(25), nullable=False),
                                              Column('reports', JSON, nullable=True),
                                              Column('paragraphs', JSON, nullable=True),
                                              Column('lastvisittime', String(25), nullable=False),
                                              Column('userid', String(60), nullable=False),
                                              Column('tenantid', String(60), nullable=False),
                                              Column('createtime', String(50), nullable=True),
                                              Column('lastmodified', DateTime, nullable=True)
                                              )

        self.topics_table = Table("topics", self.metadata,
                                  Column("topicid", String(60), primary_key=True),
                                  Column("name", String(25), nullable=False),
                                  Column("kind", String(10), nullable=True),
                                  Column("type", String(10), nullable=True),
                                  Column("description", String(50), nullable=True),
                                  Column("datasourceid", String(50), nullable=True),
                                  Column("factors", JSON, nullable=True),
                                  Column('createtime', String(50), nullable=True),
                                  Column('tenantid', String(60), nullable=False),
                                  Column('lastmodified', DateTime, nullable=True)
                                  )

        self.enums_table = Table("enums", self.metadata,
                                 Column("enumid", String(60), primary_key=True),
                                 Column("name", String(25), nullable=False),
                                 Column("description", String(25), nullable=True),
                                 Column("parentenumid", String(60), nullable=True),
                                 Column("items", JSON, nullable=True),
                                 Column('createtime', String(50), nullable=True),
                                 Column('tenantid', String(60), nullable=False),
                                 Column('lastmodified', DateTime, nullable=True)
                                 )

        self.spaces_table = Table("spaces", self.metadata,
                                  Column("spaceid", String(60), primary_key=True),
                                  Column("topicids", JSON, nullable=True),
                                  Column("groupids", JSON, nullable=True),
                                  Column("name", String(25), nullable=False),
                                  Column("description", String(25), nullable=True),
                                  Column("filters", JSON, nullable=True),
                                  Column('createtime', String(50), nullable=True),
                                  Column('tenantid', String(60), nullable=False),
                                  # Column('last_modified', DateTime, nullable=True),
                                  Column('lastmodified', DateTime, nullable=True)
                                  )

        self.console_space_favorites_table = Table("console_space_favorites", self.metadata,
                                                   Column("userid", String(60), primary_key=True),
                                                   Column("connectedspaceids", JSON, nullable=True),
                                                   Column("dashboardids", JSON, nullable=True),
                                                   Column('createtime', String(50), nullable=True),
                                                   # Column('last_modified', DateTime, nullable=True),
                                                   Column('tenantid', String(60), nullable=False),
                                                   Column('lastmodified', DateTime, nullable=True)

                                                   )

        self.console_space_graph_table = Table("console_space_graph", self.metadata,
                                               Column("connectid", String(60), primary_key=True),
                                               Column("topics", JSON, nullable=True),
                                               Column("subjects", JSON, nullable=True),
                                               Column("userid", String(60), nullable=False),
                                               Column('createtime', String(50), nullable=True),
                                               Column('tenantid', String(60), nullable=False),
                                               # Column('last_modified', DateTime, nullable=True),
                                               Column('lastmodified', DateTime, nullable=True)
                                               )

        self.console_spaces_table = Table("console_spaces", self.metadata,
                                          Column("connectid", String(60), primary_key=True),
                                          Column("topics", JSON, nullable=True),
                                          Column("groupids", JSON, nullable=True),
                                          Column("name", String(25), nullable=False),
                                          Column("spaceid", String(25), nullable=False),
                                          Column("type", String(10), nullable=True),
                                          Column('lastvisittime', DateTime, nullable=True),
                                          Column("userid", String(60), nullable=True),
                                          Column("subjectids", JSON, nullable=True),
                                          Column("subjects", JSON, nullable=True),
                                          Column("istemplate", Boolean, default=False),
                                          Column('createtime', String(50), nullable=True),
                                          Column('tenantid', String(60), nullable=False),
                                          # Column('last_modified', DateTime, nullable=True),
                                          Column('lastmodified', DateTime, nullable=True)
                                          )

        self.pipelines_table = Table("pipelines", self.metadata,
                                     Column("pipelineid", String(60), primary_key=True),
                                     Column("topicid", String(60), nullable=False),
                                     Column("name", String(50), nullable=False),
                                     Column("type", String(10), nullable=True),
                                     Column("stages", JSON, nullable=True),
                                     Column("conditional", String(5), nullable=True),
                                     Column("enabled", String(5), nullable=True),
                                     Column("on", JSON, nullable=True),
                                     Column('createtime', String(50), nullable=True),
                                     Column('tenantid', String(60), nullable=False),
                                     # Column('last_modified', DateTime, nullable=True),
                                     Column('lastmodified', DateTime, nullable=True)
                                     )

        self.pipeline_graph_table = Table("pipeline_graph", self.metadata,
                                          Column("pipelinegraphid", String(60), nullable=False),
                                          Column("name", String(50), nullable=True),
                                          Column("userid", String(60), nullable=False),
                                          Column("topics", JSON, nullable=True),
                                          Column('tenantid', String(60), nullable=False),
                                          Column('lastmodified', DateTime, nullable=True),
                                          Column('createtime', String(50), nullable=True)
                                          )

        self.console_space_subjects_table = Table("console_space_subjects", self.metadata,
                                                  Column("subjectid", String(60), primary_key=True),
                                                  Column("name", String(50), nullable=False),
                                                  Column("topiccount", Integer, nullable=True),
                                                  Column("graphicscount", Integer, nullable=True),
                                                  Column("reports", JSON, nullable=True),
                                                  Column("reportids", JSON, nullable=True),
                                                  Column('tenantid', String(60), nullable=False),
                                                  Column("dataset", JSON, nullable=True),
                                                  Column("lastvisittime", DateTime, nullable=True),
                                                  Column("createdat", String(50), nullable=True),
                                                  Column('lastmodified', DateTime, nullable=True),
                                                  Column('createtime', String(50), nullable=True)
                                                  )

        self.console_reports_table = Table("reports", self.metadata,
                                           Column("reportid", String(60), primary_key=True),
                                           Column("name", String(50), nullable=False),
                                           Column("indicators", JSON, nullable=True),
                                           Column("dimensions", JSON, nullable=True),
                                           Column("funnels", JSON, nullable=True),
                                           Column("filters", JSON, nullable=True),
                                           Column("description", String(50), nullable=True),
                                           Column("rect", JSON, nullable=True),
                                           Column("chart", JSON, nullable=True),
                                           Column("createdat", String(50), nullable=True),
                                           Column("lastvisittime", String(50), nullable=True),
                                           Column('tenantid', String(60), nullable=False),
                                           Column('lastmodified', DateTime, nullable=True),
                                           Column('createtime', String(50), nullable=True),
                                           Column('simulating', Boolean, default=False),
                                           Column('simulatedata', JSON, nullable=True),
                                           Column('simulatethumbnail', String, nullable=True)
                                           )

        self.pats_table = Table("pats", self.metadata,
                                Column("patid", String(60), primary_key=True),
                                Column("tokenid", String(50), nullable=False),
                                Column("userid", String(50), nullable=False),
                                Column("username", String(50), nullable=False),
                                Column("tenantid", String(60), nullable=False),
                                Column("note", String(50), nullable=False),
                                Column("expired", Date, nullable=True),
                                Column("permissions", JSON, nullable=True),
                                Column('lastmodified', DateTime, nullable=True),
                                Column('createtime', String(50), nullable=True)
                                )

        self.key_store_table = Table("key_stores", self.metadata,
                                     Column("tenantid", String(50), primary_key=True),
                                     Column("keyType", String(50), nullable=True),
                                     Column("params", JSON, nullable=True),
                                     Column('lastmodified', DateTime, nullable=True),
                                     Column('createtime', String(50), nullable=True)
                                     )

        self.data_sources_table = Table("data_sources", self.metadata,
                                        Column("datasourceid", String(60), primary_key=True),
                                        Column("datasourcecode", String(50), nullable=False),
                                        Column("datasourcetype", String(50), nullable=False),
                                        Column("host", String(50), nullable=True),
                                        Column("port", String(50), nullable=True),
                                        Column("username", String(60), nullable=True),
                                        Column("password", String(50), nullable=True),
                                        Column("name", String(50), nullable=True),
                                        Column("url", String(60), nullable=True),
                                        Column("tenantid", String(50), nullable=False),
                                        Column("params", JSON, nullable=True),
                                        Column('lastmodified', DateTime, nullable=True),
                                        Column('createtime', String(50), nullable=True)
                                        )

        if settings.INDEX_ON:
            self.factor_index_table = Table("factor_index", self.metadata,
                                            Column("factorindexid", String(50), primary_key=True),
                                            Column("factorid", String(50), nullable=True),
                                            Column("tenantid", String(50), nullable=True),
                                            Column("topicid", String(50), nullable=True),
                                            Column("name", String(50), nullable=True),
                                            Column("label", String(50), nullable=True),
                                            Column("topicname", String(50), nullable=True),
                                            Column("description", String(50)),
                                            Column("type", String(50)),
                                            Column('lastmodified', DateTime, nullable=True),
                                            Column('createtime', String(60), nullable=True)
                                            )

            self.pipeline_index_table = Table("pipeline_index", self.metadata,
                                              Column("pipelineindexid", String(50), primary_key=True),
                                              Column("factorid", String(50), nullable=True),
                                              Column("pipelineid", String(50), nullable=True),
                                              Column("topicid", String(50), nullable=True),
                                              Column("stageid", String(50), nullable=True),
                                              Column("unitid", String(50), nullable=True),
                                              Column("actionid", String(50), nullable=True),
                                              Column("mappingtofactorid", String(50), nullable=True),
                                              Column("mappingtotopicid", String(50), nullable=True),
                                              Column("sourcefromfactorid", String(50), nullable=True),
                                              Column("sourcefromtopicid", String(50), nullable=True),
                                              Column("pipelinename", String(60)),
                                              Column("stagename", String(60)),
                                              Column("unitname", String(60)),
                                              Column("reftype", String(50)),
                                              Column("tenantid", String(50), nullable=True),
                                              Column('lastmodified', DateTime, nullable=True),
                                              Column('createtime', String(60), nullable=True)
                                              )

    def get_table_by_name(self, table_name):
        return self.get_meta_table(table_name)

    def get_meta_table(self, table_name):
        if table_name == "users":
            return self.users_table
        elif table_name == "console_space_last_snapshot":
            return self.console_space_last_snapshot_table
        elif table_name == "console_dashboards":
            return self.console_dashboards_table
        elif table_name == "topics":
            return self.topics_table
        elif table_name == "enums":
            return self.enums_table
        elif table_name == "spaces":
            return self.spaces_table
        elif table_name == "console_space_favorites":
            return self.console_space_favorites_table
        elif table_name == "console_space_graph":
            return self.console_space_graph_table
        elif table_name == "console_spaces":
            return self.console_spaces_table
        elif table_name == "user_groups":
            return self.user_groups_table
        elif table_name == "pipelines":
            return self.pipelines_table
        elif table_name == "pipeline_graph":
            return self.pipeline_graph_table
        elif table_name == "console_space_subjects":
            return self.console_space_subjects_table
        elif table_name == "console_reports":
            return self.console_reports_table
        elif table_name == "tenants":
            return self.tenants_table
        elif table_name == "pats":
            return self.pats_table
        elif table_name == "data_sources":
            return self.data_sources_table
        elif table_name == "external_writer":
            return self.external_writer
        elif table_name == "key_stores":
            return self.key_store_table
        elif table_name == "factor_index":
            return self.factor_index_table
        elif table_name == "pipeline_index":
            return self.pipeline_index_table
        else:
            raise Exception(" table_name is not a valid table name")
