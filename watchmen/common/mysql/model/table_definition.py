from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base

from watchmen.common.mysql.mysql_engine import engine

Base = declarative_base()


class topics(Base):
    __tablename__ = "topics"

    topicId = Column(String, primary_key=True)
    name = Column(String)
    kind = Column(String)
    type = Column(String)
    description = Column(String)
    version = Column(Integer, nullable=False)
    factors = Column(JSON)
    createTime = Column(String)
    last_modified = Column(DateTime)

    __mapper_args__ = {
        "version_id_col": version
    }


class console_space_subjects(Base):
    __tablename__ = 'console_space_subjects'

    subjectId = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    topicCount = Column(Integer, nullable=False)
    graphicsCount = Column(Integer, nullable=False)
    lastVisitTime = Column(DateTime)
    createdAt = Column(String, nullable=True)
    reports = Column(JSON)
    reportIds = Column(JSON)
    dataset = Column(JSON)
    version = Column(Integer, nullable=False)
    createTime = Column(String)
    last_modified = Column(DateTime)

    __mapper_args__ = {
        "version_id_col": version
    }


class pipelines(Base):
    __tablename__ = 'pipelines'

    pipelineId = Column(String, primary_key=True)
    topicId = Column(String, nullable=True)
    name = Column(String, nullable=True)
    type = Column(String, nullable=True)
    stages = Column(JSON)
    enabled = Column(Boolean)
    version = Column(Integer, nullable=False)

    __mapper_args__ = {
        "version_id_col": version
    }


def get_table_model(collection_name):
    if collection_name == 'topics':
        return topics
    elif collection_name == 'console_space_subjects':
        return console_space_subjects
    elif collection_name == 'pipelines':
        return pipelines


def parse_obj(base_model, result):
    model = base_model()
    for attr, value in model.__dict__.items():
        if attr[:1] != '_':
            setattr(model, attr, getattr(result, attr))
    return model


def count_table(table_name):
    primary_key = get_primary_key(table_name)
    session = Session(engine, future=True)
    stmt = 'SELECT count(%s) AS count FROM %s' % (primary_key, table_name)
    result = session.execute(stmt)
    for row in result:
        return row[0]


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
    elif table_name == 'enums':
        return 'enumId'
    elif table_name == 'pipelines':
        return 'pipelineId'
    elif table_name == 'pipeline_graph':
        return 'userId'
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
