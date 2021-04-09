from watchmen.common.pagination import Pagination
from watchmen.common.storage.storage_template import insert_one, update_one, find_by_id, find_, delete_one, page_
from watchmen.console_space.model.console_space import Report

CONSOLE_REPORTS = "console_reports"


# template = find_template()


def create_report(report):
    # return template.create(CONSOLE_REPORTS, report, Report)
    return insert_one(report, Report, CONSOLE_REPORTS)


def save_subject_report(report):
    # return template.update_one(CONSOLE_REPORTS, {"reportId": report.reportId}, report, Report)
    return update_one(report, Report, CONSOLE_REPORTS)


def load_report_by_id(report_id):
    # return template.find_one(CONSOLE_REPORTS, {"reportId": report_id}, Report)
    return find_by_id(report_id, Report, CONSOLE_REPORTS)


def load_reports_by_ids(report_ids):
    # return template.find(CONSOLE_REPORTS, {"reportId": {"$in": report_ids}}, Report)
    return find_({"reportId": {"in": report_ids}}, Report, CONSOLE_REPORTS)


def delete_report_by_id(report_id):
    # template.delete_one(CONSOLE_REPORTS, {"reportId": report_id})
    delete_one(report_id, CONSOLE_REPORTS)


def import_report_to_db(report):
    # template.create(CONSOLE_REPORTS, report, Report)
    insert_one(report, Report, CONSOLE_REPORTS)


def query_report_list_with_pagination(query_name: str, pagination: Pagination):
    '''
    return template.query_with_pagination(CONSOLE_REPORTS, pagination, Report,
                                          query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])
    '''
    query_dict = {"name": {"like": query_name}}
    sort_dict = [("last_modified", "desc")]
    return page_(query_dict, sort_dict, pagination, Report, CONSOLE_REPORTS)
