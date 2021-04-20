import json

from sqlalchemy import Table, Column, String, JSON, Date, Text, CLOB, text

from watchmen.common.oracle.oracle_engine import engine


def parse_obj(base_model, result, table):
    model = base_model()
    for attr, value in model.__dict__.items():
        if attr[:1] != '_':
            if isinstance(table.c[attr.lower()].type, CLOB):
                if result[attr.upper()] is not None:
                    setattr(model, attr, json.loads(result[attr.upper()]))
                else:
                    setattr(model, attr, None)
            else:
                setattr(model, attr, result[attr.upper()])
    return model


def get_db_primary_key(table_name):
    if table_name == 'topics':
        return 'topicid'
    elif table_name == 'console_space_subjects':
        return 'subjectId'
    elif table_name == 'pipelines':
        return 'pipelineId'
    elif table_name == 'users':
        return 'userId'
    elif table_name == 'console_dashboards':
        return 'dashboardId'
    elif table_name == 'enum_items':
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
    elif table_name == 'enums':
        return 'enumId'


def count_table(table_name):
    primary_key = get_db_primary_key(table_name)
    stmt = 'SELECT count(%s) AS count FROM %s' % (primary_key, table_name)
    with engine.connect() as conn:
        cursor = conn.execute(text(stmt)).cursor
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        result = cursor.fetchone()
    return result['COUNT']
