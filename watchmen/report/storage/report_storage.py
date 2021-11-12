from watchmen.common.model.user import User
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.console_space.model.console_space import Report
from watchmen.database.storage.storage_template import insert_one, update_one, find_, page_, \
    delete_by_id, find_one

CONSOLE_REPORTS = "console_reports"


def create_report(report: Report):
    report.reportId = get_surrogate_key()
    return insert_one(report, Report, CONSOLE_REPORTS)


def save_subject_report(report):
    return update_one(report, Report, CONSOLE_REPORTS)


def load_report_by_id(report_id, current_user):
    return find_one({"and": [{"reportId": report_id}, {"tenantId": current_user.tenantId}]}, Report, CONSOLE_REPORTS)


def load_reports_by_ids(report_ids, current_user):
    return find_({"and": [{"reportId": {"in": report_ids}}, {"tenantId": current_user.tenantId}]}, Report,
                 CONSOLE_REPORTS)


def delete_report_by_id(report_id):
    # template.delete_one(CONSOLE_REPORTS, {"reportId": report_id})
    delete_by_id(report_id, CONSOLE_REPORTS)


def import_report_to_db(report):
    return insert_one(report, Report, CONSOLE_REPORTS)


def query_report_list_with_pagination(query_name: str, pagination: Pagination, current_user: User):
    '''
    return template.query_with_pagination(CONSOLE_REPORTS, pagination, Report,
                                          query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])
    '''
    query_dict = {"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}
    sort_dict = [("last_modified", "desc")]
    return page_(query_dict, sort_dict, pagination, Report, CONSOLE_REPORTS)
