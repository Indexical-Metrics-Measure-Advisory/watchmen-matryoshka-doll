from sqlalchemy import MetaData, Table, Column, String, CLOB, Date, DateTime, Integer

from watchmen_boot.config.config import settings

metadata = MetaData()


def get_primary_key(table_name):
    return get_pid(table_name)



def get_pid(table_name):
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


users_table = Table("users", metadata,
                    Column('userid', String(60), primary_key=True),
                    Column('name', String(45), nullable=False),
                    Column('nickname', String(45), nullable=True),
                    Column('password', String(100), nullable=True),
                    Column('is_active', String(5), nullable=True),
                    Column('groupids', CLOB, nullable=True),
                    Column('role', String(45), nullable=True),
                    Column('tenantid', String(60), nullable=False),
                    Column('createtime', String(50), nullable=True),
                    Column('lastmodified', Date, nullable=True)
                    )

user_groups_table = Table("user_groups", metadata,
                          Column('usergroupid', String(60), primary_key=True),
                          Column('name', String(45), nullable=False),
                          Column('description', String(45), nullable=True),
                          Column('userids', CLOB, nullable=True),
                          Column('spaceids', CLOB, nullable=True),
                          Column('tenantid', String(60), nullable=False),
                          Column('createtime', String(50), nullable=True),
                          Column('lastmodified', Date, nullable=True)
                          )

external_writer_table = Table("external_writer", metadata,
                              Column('writerid', String(50), primary_key=True),
                              Column('writercode', String(50), nullable=False),
                              Column('type', String(50), nullable=False),
                              Column('pat', String(50), nullable=False),
                              Column('url', String(50), nullable=False),
                              Column('tenantid', String(60), nullable=True),
                              Column('createtime', String(50), nullable=True),
                              Column('lastmodified', Date, nullable=True)
                              )

console_space_last_snapshot_table = Table("console_space_last_snapshot", metadata,
                                          Column('userid', String(60), primary_key=True),
                                          Column('language', String(5), nullable=True),
                                          Column('lastdashboardid', String(25), nullable=True),
                                          Column('admindashboardid', String(25), nullable=True),
                                          Column('favoritepin', String(5), nullable=True),
                                          Column('tenantid', String(60), nullable=False),
                                          Column('createtime', String(50), nullable=True),
                                          Column('lastmodified', Date, nullable=True)
                                          )

console_dashboards_table = Table("console_dashboards", metadata,
                                 Column('dashboardid', String(60), primary_key=True),
                                 Column('name', String(25), nullable=False),
                                 Column('reports', CLOB, nullable=True),
                                 Column('paragraphs', CLOB, nullable=True),
                                 Column('lastvisittime', String(25), nullable=False),
                                 Column('userid', String(60), nullable=False),
                                 Column('tenantid', String(60), nullable=False),
                                 Column('createtime', String(50), nullable=True),
                                 Column('lastmodified', DateTime, nullable=True)
                                 )

topics_table = Table("topics", metadata,
                     Column("topicid", String(60), primary_key=True),
                     Column("name", String(25), nullable=False),
                     Column("kind", String(10), nullable=True),
                     Column("type", String(10), nullable=True),
                     Column("description", String(250), nullable=True),
                     Column("factors", CLOB, nullable=True),
                     Column("datasourceid", String(60), nullable=True),
                     Column('tenantid', String(60), nullable=False),
                     Column('createtime', String(50), nullable=True),
                     # Column('last_modified', DateTime, nullable=True),
                     Column('lastmodified', DateTime, nullable=True)
                     )

enums_table = Table("enums", metadata,
                    Column("enumid", String(60), primary_key=True),
                    Column("name", String(25), nullable=False),
                    Column("description", String(25), nullable=True),
                    Column("parentenumid", String(60), nullable=True),
                    Column("items", CLOB, nullable=True),
                    Column('tenantid', String(60), nullable=False),
                    Column('createtime', String(50), nullable=True),
                    Column('lastmodified', DateTime, nullable=True)
                    )

spaces_table = Table("spaces", metadata,
                     Column("spaceid", String(60), primary_key=True),
                     Column("topicids", CLOB, nullable=True),
                     Column("groupids", CLOB, nullable=True),
                     Column("name", String(25), nullable=False),
                     Column("description", String(25), nullable=True),
                     Column("filters", CLOB, nullable=True),
                     Column('tenantid', String(60), nullable=False),
                     Column('createtime', String(50), nullable=True),
                     # Column('last_modified', DateTime, nullable=True),
                     Column('lastmodified', DateTime, nullable=True)
                     )

console_space_favorites_table = Table("console_space_favorites", metadata,
                                      Column("userid", String(60), primary_key=True),
                                      Column("connectedspaceids", CLOB, nullable=True),
                                      Column("dashboardids", CLOB, nullable=True),
                                      Column('tenantid', String(60), nullable=False),
                                      Column('createtime', String(50), nullable=True),
                                      # Column('last_modified', DateTime, nullable=True),
                                      Column('lastmodified', DateTime, nullable=True)
                                      )

console_space_graph_table = Table("console_space_graph", metadata,
                                  Column("connectid", String(60), primary_key=True),
                                  Column("topics", CLOB, nullable=True),
                                  Column("subjects", CLOB, nullable=True),
                                  Column("userid", String(60), nullable=False),
                                  Column('tenantid', String(60), nullable=False),
                                  Column('createtime', String(50), nullable=True),
                                  # Column('last_modified', DateTime, nullable=True),
                                  Column('lastmodified', DateTime, nullable=True)
                                  )

console_spaces_table = Table("console_spaces", metadata,
                             Column("spaceid", String(60), primary_key=True),
                             Column("topics", CLOB, nullable=True),
                             Column("groupids", CLOB, nullable=True),
                             Column("name", String(25), nullable=False),
                             Column("connectid", String(25), nullable=False),
                             Column("type", String(10), nullable=True),
                             Column('lastvisittime', DateTime, nullable=True),
                             Column("userid", String(60), nullable=True),
                             Column("subjectids", CLOB, nullable=True),
                             Column("istemplate", String(5), default=False),
                             Column("subjects", CLOB, nullable=True),
                             Column('tenantid', String(60), nullable=False),
                             Column('createtime', String(50), nullable=True),
                             Column('lastmodified', DateTime, nullable=True)
                             )

pipelines_table = Table("pipelines", metadata,
                        Column("pipelineid", String(60), primary_key=True),
                        Column("topicid", String(60), nullable=False),
                        Column("name", String(25), nullable=False),
                        Column("type", String(10), nullable=True),
                        Column("stages", CLOB, nullable=True),
                        Column("conditional", String(5), nullable=True),
                        Column("enabled", String(5), nullable=True),
                        Column("on", CLOB, nullable=True),
                        Column('tenantid', String(60), nullable=False),
                        Column('createtime', String(50), nullable=True),
                        # Column('last_modified', DateTime, nullable=True),
                        Column('lastmodified', DateTime, nullable=True)
                        )

pipeline_graph_table = Table("pipeline_graph", metadata,
                             Column("pipelinegraphid", String(60), nullable=False),
                             Column("name", String(50), nullable=True),
                             Column("userid", String(60), nullable=False),
                             Column("topics", CLOB, nullable=True),
                             Column('tenantid', String(60), nullable=False),
                             Column('lastmodified', DateTime, nullable=True),
                             Column('createtime', String(50), nullable=True)
                             )

console_space_subjects_table = Table("console_space_subjects", metadata,
                                     Column("subjectid", String(60), primary_key=True),
                                     Column("name", String(50), nullable=False),
                                     Column("topiccount", Integer, nullable=True),
                                     Column("graphicscount", Integer, nullable=True),
                                     Column("reports", CLOB, nullable=True),
                                     Column("reportids", CLOB, nullable=True),
                                     Column("dataset", CLOB, nullable=True),
                                     Column('tenantid', String(60), nullable=False),
                                     Column("lastvisittime", DateTime, nullable=True),
                                     Column("createdat", String(50), nullable=True),
                                     # Column('lastmodifytime', DateTime, nullable=True),
                                     Column('lastmodified', DateTime, nullable=True),
                                     Column('createtime', String(50), nullable=True)
                                     )

console_reports_table = Table("reports", metadata,
                              Column("reportid", String(60), primary_key=True),
                              Column("name", String(50), nullable=False),
                              Column("indicators", CLOB, nullable=True),
                              Column("dimensions", CLOB, nullable=True),
                              Column("funnels", CLOB, nullable=True),
                              Column("filters", CLOB, nullable=True),
                              Column("description", String(50), nullable=True),
                              Column("rect", CLOB, nullable=True),
                              Column("chart", CLOB, nullable=True),
                              Column('tenantid', String(60), nullable=False),
                              Column("createdat", String(50), nullable=True),
                              Column("lastvisittime", String(50), nullable=True),
                              Column('lastmodified', DateTime, nullable=True),
                              Column('createtime', String(50), nullable=True),
                              Column('simulating', String(5), default=False),
                              Column('simulatedata', CLOB, nullable=True),
                              Column('simulatethumbnail', CLOB, nullable=True)
                              )

pats_table = Table("pats", metadata,
                   Column("patid", String(60), primary_key=True),
                   Column("tokenid", String(50), nullable=False),
                   Column("userid", String(50), nullable=False),
                   Column("username", String(50), nullable=False),
                   Column("tenantid", String(60), nullable=False),
                   Column("note", String(50), nullable=False),
                   Column("expired", Date, nullable=True),
                   Column("permissions", CLOB, nullable=True),
                   Column('lastmodified', DateTime, nullable=True),
                   Column('createtime', String(50), nullable=True)
                   )

tenants_table = Table("tenants", metadata,
                      Column("tenantid", String(60), primary_key=True),
                      Column("name", String(50), nullable=True),
                      Column('lastmodified', DateTime, nullable=True),
                      Column('createtime', String(50), nullable=True)
                      )

key_store_table = Table("key_stores", metadata,
                        Column("tenantid", String(50), primary_key=True),
                        Column("keyType", String(50), nullable=True),
                        Column("params", CLOB, nullable=True),
                        Column('lastmodified', DateTime, nullable=True),
                        Column('createtime', String(50), nullable=True)
                        )

data_sources_table = Table("data_sources", metadata,
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
                           Column("params", CLOB, nullable=True),
                           Column('lastmodified', DateTime, nullable=True),
                           Column('createtime', String(50), nullable=True)
                           )

if settings.INDEX_ON:
    factor_index_table = Table("factor_index", metadata,
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

    pipeline_index_table = Table("pipeline_index", metadata,
                                 Column("pipelineindexid", String(50), primary_key=True),
                                 Column("factorid", String(50)),
                                 Column("pipelineid", String(50)),
                                 Column("topicid", String(50)),
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
                                 Column("reftype", String(50), nullable=True),
                                 Column("tenantid", String(50), nullable=True),
                                 Column('lastmodified', DateTime, nullable=True),
                                 Column('createtime', String(60), nullable=True)
                                 )


def get_table_by_name(table_name):
    if table_name == "users":
        return users_table
    elif table_name == "console_space_last_snapshot":
        return console_space_last_snapshot_table
    elif table_name == "console_dashboards":
        return console_dashboards_table
    elif table_name == "topics":
        return topics_table
    elif table_name == "enums":
        return enums_table
    elif table_name == "spaces":
        return spaces_table
    elif table_name == "console_space_favorites":
        return console_space_favorites_table
    elif table_name == "console_space_graph":
        return console_space_graph_table
    elif table_name == "console_spaces":
        return console_spaces_table
    elif table_name == "user_groups":
        return user_groups_table
    elif table_name == "pipelines":
        return pipelines_table
    elif table_name == "pipeline_graph":
        return pipeline_graph_table
    elif table_name == "console_space_subjects":
        return console_space_subjects_table
    elif table_name == "console_reports":
        return console_reports_table
    elif table_name == "pats":
        return pats_table
    elif table_name == "tenants":
        return tenants_table
    elif table_name == "data_sources":
        return data_sources_table
    elif table_name == "external_writer":
        return external_writer_table
    elif table_name == "key_stores":
        return key_store_table
    elif table_name == "factor_index":
        return factor_index_table
    elif table_name == "pipeline_index":
        return pipeline_index_table
    else:
        raise Exception("table_name does not exist {}".format(table_name))
