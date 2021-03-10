from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.console_space.model.console_space import Report

db = get_client()
console_reports = db.get_collection('console_reports')


def create_report(report):
    console_reports.insert_one(report.dict())
    return Report.parse_obj(report)


def save_subject_report(report):
    console_reports.update_one({"reportId": report.reportId}, {"$set": report.dict()})
    return report


def create_dataset_reports(reports):
    console_reports.insert_many(reports)


def load_report_by_id(report_id):
    result = console_reports.find_one({"reportId": report_id})
    if result is None:
        return None
    else:
        return Report.parse_obj(result)


def load_reports_by_ids(report_ids):
    results = console_reports.find({"reportId": {"$in": report_ids}})
    return list(results)


def delete_report_by_id(report_id):
    console_reports.delete_one({"reportId": report_id})


def import_report_to_db(report):
    console_reports.insert_one(report)
