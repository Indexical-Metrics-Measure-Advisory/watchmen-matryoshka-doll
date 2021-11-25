from watchmen.common.utils.data_utils import add_tenant_id_to_model
from model.model.console_space.console_space import ConsoleSpace, ConsoleSpaceSubject
from watchmen.console_space.storage.console_space_storage import load_console_space_by_subject_id, save_console_space, \
    load_console_space_by_id, delete_console_space_storage
from watchmen.console_space.storage.console_subject_storage import delete_console_subject_by_id, \
    delete_console_subject_by_ids, load_console_subject_by_id, create_console_subject_to_storage, \
    load_console_subject_by_report_id
from model.model.report.report import Report
from watchmen.report.storage.report_storage import load_report_by_id, create_report


def delete_console_subject(subject_id, current_user):
    delete_console_subject_by_id(subject_id)
    console_space = load_console_space_by_subject_id(subject_id, current_user)
    console_space.subjectIds.remove(subject_id)
    delete_console_subject_by_id(subject_id)
    save_console_space(console_space)


def delete_console_space_and_sub_data(connect_id, current_user):
    console_space = load_console_space_by_id(connect_id, current_user)
    if console_space.subjectIds:
        delete_console_subject_by_ids(console_space.subjectIds)
    delete_console_space_storage(connect_id)


def load_space_list_by_dashboard(dashboard, current_user):
    subject_dict = {}
    space_dict = {}
    report_dict = {}
    space_list = []
    if dashboard is not None:
        for dashboard_report in dashboard.reports:
            report = load_report_by_id(dashboard_report.reportId, current_user)
            report_dict[report.reportId] = report
            console_subject = load_console_subject_by_report_id(report.reportId, current_user)
            subject_dict[console_subject.subjectId] = console_subject
            console_space = load_console_space_by_subject_id(console_subject.subjectId, current_user)
            space_dict[console_space.spaceId] = console_space
        for key, space in space_dict.items():
            for subjectId in space.subjectIds:
                if subjectId in subject_dict:
                    subject = subject_dict[subjectId]
                    for reportId in subject.reportIds:
                        if reportId in report_dict:
                            report = report_dict[reportId]
                            subject.reports.append(report)
                    space.subjects.append(subject)
            space_list.append(space)
        return {"dashboard": dashboard, "connectedSpaces": space_list}


def copy_template_to_console_space(template_ids, console_space: ConsoleSpace, current_user):
    if template_ids:
        for template_id in template_ids.split(","):
            template_space = load_console_space_by_id(template_id, current_user)
            for subject_id in template_space.subjectIds:
                subject: ConsoleSpaceSubject = load_console_subject_by_id(subject_id, current_user)
                subject.subjectId = None
                subject = add_tenant_id_to_model(subject, current_user)
                new_report_ids = []
                for report_id in subject.reportIds:
                    report: Report = load_report_by_id(report_id, current_user)
                    report = add_tenant_id_to_model(report, current_user)
                    report = create_report(report)
                    subject.reports.append(report)
                    new_report_ids.append(report.reportId)
                subject.reportIds = new_report_ids
                subject = create_console_subject_to_storage(subject)
                console_space.subjectIds.append(subject.subjectId)
                console_space.subjects.append(subject)

    return console_space
