from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.console_space.model.console_space import Report

db = get_client()
console_report_collection = db.get_collection('console_report')


def create_report(report):
    console_report_collection.insert_one(report.dict())
    return Report.parse_obj(report)


def save_subject_report(report):
    console_report_collection.update_one({"reportId": report.reportId}, {"$set": report.dict()})
    return report


def create_dataset_reports(reports):
    console_report_collection.insert_many(reports)


def load_report_by_id(report_id):
    result = console_report_collection.find_one({"reportId": report_id})
    return Report.parse_obj(result)


def load_reports_by_ids(report_ids):
    results = console_report_collection.find({"reportId":{"$in":report_ids}})
    return list(results)


def delete_report_by_id(report_id):
    console_report_collection.delete_one({"reportId": report_id})
