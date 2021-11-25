from model.model.common.pagination import Pagination
from model.model.common.user import User
from model.model.report.report import Report

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.database.find_storage_template import find_storage_template

CONSOLE_REPORTS = "console_reports"

storage_template = find_storage_template()


def create_report(report: Report):
    report.reportId = get_surrogate_key()
    return storage_template.insert_one(report, Report, CONSOLE_REPORTS)


def save_subject_report(report):
    return storage_template.update_one(report, Report, CONSOLE_REPORTS)


def load_report_by_id(report_id, current_user):
    return storage_template.find_one({"and": [{"reportId": report_id}, {"tenantId": current_user.tenantId}]}, Report,
                                     CONSOLE_REPORTS)


def load_reports_by_ids(report_ids, current_user):
    return storage_template.find_({"and": [{"reportId": {"in": report_ids}}, {"tenantId": current_user.tenantId}]},
                                  Report,
                                  CONSOLE_REPORTS)


def delete_report_by_id(report_id):
    # template.delete_one(CONSOLE_REPORTS, {"reportId": report_id})
    storage_template.delete_by_id(report_id, CONSOLE_REPORTS)


def import_report_to_db(report):
    return storage_template.insert_one(report, Report, CONSOLE_REPORTS)


def query_report_list_with_pagination(query_name: str, pagination: Pagination, current_user: User):
    '''
    return template.query_with_pagination(CONSOLE_REPORTS, pagination, Report,
                                          query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])
    '''
    query_dict = {"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}
    sort_dict = [("last_modified", "desc")]
    return storage_template.page_(query_dict, sort_dict, pagination, Report, CONSOLE_REPORTS)
