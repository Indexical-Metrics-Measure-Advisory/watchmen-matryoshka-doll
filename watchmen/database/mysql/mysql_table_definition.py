from sqlalchemy import MetaData, Table, Column, String, Date, DateTime, Integer, JSON, Boolean
from watchmen.database.mysql.mysql_engine import engine


metadata = MetaData()

users_table = Table("users", metadata,
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

tenants_table = Table("tenants", metadata,
                      Column('tenantid', String(60), primary_key=True),
                      Column('name', String(45), nullable=False),
                      Column('createtime', String(50), nullable=True),
                      Column('lastmodified', Date, nullable=True)
                      )

user_groups_table = Table("user_groups", metadata,
                          Column('usergroupid', String(60), primary_key=True),
                          Column('name', String(45), nullable=False),
                          Column('description', String(45), nullable=True),
                          Column('userids', JSON, nullable=True),
                          Column('spaceids', JSON, nullable=True),
                          Column('createtime', String(50), nullable=True),
                          Column('tenantid', String(60), nullable=True),
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
                                 Column('reports', JSON, nullable=True),
                                 Column('paragraphs', JSON, nullable=True),
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
                     Column("description", String(50), nullable=True),
                     Column("factors", JSON, nullable=True),
                     Column('createtime', String(50), nullable=True),
                     Column('tenantid', String(60), nullable=False),
                     # Column('last_modified', DateTime, nullable=True),
                     Column('lastmodified', DateTime, nullable=True)
                     )

enums_table = Table("enums", metadata,
                    Column("enumid", String(60), primary_key=True),
                    Column("name", String(25), nullable=False),
                    Column("description", String(25), nullable=True),
                    Column("parentenumid", String(60), nullable=True),
                    Column("items", JSON, nullable=True),
                    Column('createtime', String(50), nullable=True),
                    Column('tenantid', String(60), nullable=False),
                    Column('lastmodified', DateTime, nullable=True)
                    )

spaces_table = Table("spaces", metadata,
                     Column("spaceid", String(60), primary_key=True),
                     Column("topicids", JSON, nullable=True),
                     Column("groupids", JSON, nullable=True),
                     Column("name", String(25), nullable=False),
                     Column("description", String(25), nullable=True),
                     Column('createtime', String(50), nullable=True),
                     Column('tenantid', String(60), nullable=False),
                     # Column('last_modified', DateTime, nullable=True),
                     Column('lastmodified', DateTime, nullable=True)
                     )

console_space_favorites_table = Table("console_space_favorites", metadata,
                                      Column("userid", String(60), primary_key=True),
                                      Column("connectedspaceids", JSON, nullable=True),
                                      Column("dashboardids", JSON, nullable=True),
                                      Column('createtime', String(50), nullable=True),
                                      # Column('last_modified', DateTime, nullable=True),
                                      Column('tenantid', String(60), nullable=False),
                                      Column('lastmodified', DateTime, nullable=True)

                                      )

console_space_graph_table = Table("console_space_graph", metadata,
                                  Column("connectid", String(60), primary_key=True),
                                  Column("topics", JSON, nullable=True),
                                  Column("subjects", JSON, nullable=True),
                                  Column("userid", String(60), nullable=False),
                                  Column('createtime', String(50), nullable=True),
                                  Column('tenantid', String(60), nullable=False),
                                  # Column('last_modified', DateTime, nullable=True),
                                  Column('lastmodified', DateTime, nullable=True)
                                  )

console_spaces_table = Table("console_spaces", metadata,
                             Column("spaceid", String(60), primary_key=True),
                             Column("topics", JSON, nullable=True),
                             Column("groupids", JSON, nullable=True),
                             Column("name", String(25), nullable=False),
                             Column("connectid", String(25), nullable=False),
                             Column("type", String(10), nullable=True),
                             Column('lastvisittime', DateTime, nullable=True),
                             Column("userid", String(60), nullable=True),
                             Column("subjectids", JSON, nullable=True),
                             Column("subjects", JSON, nullable=True),
                             Column("istemplate",Boolean,default=False),
                             Column('createtime', String(50), nullable=True),
                             Column('tenantid', String(60), nullable=False),
                             # Column('last_modified', DateTime, nullable=True),
                             Column('lastmodified', DateTime, nullable=True)
                             )

pipelines_table = Table("pipelines", metadata,
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

pipeline_graph_table = Table("pipeline_graph", metadata,
                             Column("pipelinegraphid", String(60), nullable=False),
                             Column("name", String(50), nullable=True),
                             Column("userid", String(60), nullable=False),
                             Column("topics", JSON, nullable=True),
                             Column('tenantid', String(60), nullable=False),
                             Column('lastmodified', DateTime, nullable=True),
                             Column('createtime', String(50), nullable=True)
                             )

console_space_subjects_table = Table("console_space_subjects", metadata,
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

console_reports_table = Table("reports", metadata,
                              Column("reportid", String(60), primary_key=True),
                              Column("name", String(50), nullable=False),
                              Column("indicators", JSON, nullable=True),
                              Column("dimensions", JSON, nullable=True),
                              Column("description", String(50), nullable=True),
                              Column("rect", JSON, nullable=True),
                              Column("chart", JSON, nullable=True),
                              Column("createdat", String(50), nullable=True),
                              Column("lastvisittime", String(50), nullable=True),
                              Column('tenantid', String(60), nullable=False),
                              Column('lastmodified', DateTime, nullable=True),
                              Column('createtime', String(50), nullable=True)
                              )

pats_table = Table("pats", metadata,
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


def get_table_by_name(table_name):
    return get_meta_table(table_name)


def get_meta_table(table_name):
    if table_name == "users":
        table = users_table
    elif table_name == "console_space_last_snapshot":
        table = console_space_last_snapshot_table
    elif table_name == "console_dashboards":
        table = console_dashboards_table
    elif table_name == "topics":
        table = topics_table
    elif table_name == "enums":
        table = enums_table
    elif table_name == "spaces":
        table = spaces_table
    elif table_name == "console_space_favorites":
        table = console_space_favorites_table
    elif table_name == "console_space_graph":
        table = console_space_graph_table
    elif table_name == "console_spaces":
        table = console_spaces_table
    elif table_name == "user_groups":
        table = user_groups_table
    elif table_name == "pipelines":
        table = pipelines_table
    elif table_name == "pipeline_graph":
        table = pipeline_graph_table
    elif table_name == "console_space_subjects":
        table = console_space_subjects_table
    elif table_name == "console_reports":
        table = console_reports_table
    elif table_name == "tenants":
        table = tenants_table
    elif table_name == "pats":
        table = pats_table
    return table


def get_topic_table_by_name(table_name):
    table = Table(table_name, metadata, extend_existing=False, autoload=True, autoload_with=engine)
    return table
