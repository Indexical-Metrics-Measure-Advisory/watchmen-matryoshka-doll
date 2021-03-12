from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.console_space.model.console_space import Report
#
# db = get_client()
# console_reports = db.get_collection('console_reports')


CONSOLE_REPORTS = "console_reports"

template = find_template()


def create_report(report):
    # console_reports.insert_one(report.dict())
    # return Report.parse_obj(report)
    return  template.create(CONSOLE_REPORTS,report,Report)


def save_subject_report(report):
    # console_reports.update_one({"reportId": report.reportId}, {"$set": report.dict()})
    # return report
    return template.update_one(CONSOLE_REPORTS,{"reportId": report.reportId},report,Report)


# def create_dataset_reports(reports):
#     console_reports.insert_many(reports)

def load_report_by_id(report_id):
    # result = console_reports.find_one({"reportId": report_id})
    # if result is None:
    #     return None
    # else:
    #     return Report.parse_obj(result)
    return template.find_one(CONSOLE_REPORTS,{"reportId": report_id},Report)


def load_reports_by_ids(report_ids):
    # results = console_reports.find({"reportId": {"$in": report_ids}})
    # return list(results)
    return template.find(CONSOLE_REPORTS,{"reportId": {"$in": report_ids}},Report)


def delete_report_by_id(report_id):
    # console_reports.delete_one({"reportId": report_id})
    template.delete_one(CONSOLE_REPORTS,{"reportId": report_id})


def import_report_to_db(report):
    # console_reports.insert_one(report)
    template.create(CONSOLE_REPORTS,report,Report)
