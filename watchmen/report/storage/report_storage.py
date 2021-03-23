import pymongo
from bson import regex

from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.console_space.model.console_space import Report

CONSOLE_REPORTS = "console_reports"

template = find_template()


def create_report(report):
    return template.create(CONSOLE_REPORTS, report, Report)


def save_subject_report(report):
    return template.update_one(CONSOLE_REPORTS, {"reportId": report.reportId}, report, Report)


def load_report_by_id(report_id):
    return template.find_one(CONSOLE_REPORTS, {"reportId": report_id}, Report)


def load_reports_by_ids(report_ids):
    return template.find(CONSOLE_REPORTS, {"reportId": {"$in": report_ids}}, Report)


def delete_report_by_id(report_id):
    template.delete_one(CONSOLE_REPORTS, {"reportId": report_id})


def import_report_to_db(report):
    template.create(CONSOLE_REPORTS, report, Report)


def query_report_list_with_pagination(query_name: str, pagination: Pagination):
    return template.query_with_pagination(CONSOLE_REPORTS, pagination, Report,
                                          query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])
