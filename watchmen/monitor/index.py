from watchmen.common.presto.presto_client import get_connection
from watchmen.console_space.model.console_space import ConsoleSpaceSubjectChartDataSet
from watchmen.monitor.model.presto_monitor import PrestoSQLStatus
from watchmen.monitor.presto.index import load_query_status_from_presto
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_id


def load_slow_pipeline_status(top_n):
    sql ="SELECT complete_time,status,pipelineId FROM monitor_pipeline ORDER BY complete_time DESC LIMIT {0}".format(top_n)
    cur = get_connection().cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    results =[]
    for row in rows:
        row[0]=str(row[0])+"ms"
        row[2] = load_pipeline_by_id(row[2]).name
        results.append(row)
    return results


def is_system_subject(subject_id):
    if subject_id == "SYS_001":
        return True
    else:
        return False


def load_query_status():
    result = []
    sql_status_list = load_query_status_from_presto()
    for sql_status in sql_status_list:
        presto_sql_status = PrestoSQLStatus()
        presto_sql_status.query = sql_status["query"]
        presto_sql_status.executionTime =  sql_status["queryStats"]["executionTime"]
        presto_sql_status.rawInputPositions = sql_status["queryStats"]["rawInputPositions"]
        presto_sql_status.state = sql_status["state"]
        result.append(presto_sql_status)
    return result


def load_system_monitor_chart_data(subject_id,chart_id):
    if chart_id=="TOP_10_SQL":
        return ConsoleSpaceSubjectChartDataSet(data=load_query_status())
    elif chart_id=="TOP_10_SLOW_PIPELINE":
        return ConsoleSpaceSubjectChartDataSet(data=load_slow_pipeline_status(10))