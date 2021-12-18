from model.model.console_space.console_space import ConsoleSpaceSubject

from watchmen_boot.guid.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
# from watchmen.database.storage.storage_template import insert_one, find_, update_one, delete_, \
#     find_one, update_one_first, delete_by_id
from watchmen.database.find_storage_template import find_storage_template

CONSOLE_SPACE_SUBJECTS = "console_space_subjects"

storage_template = find_storage_template()


def create_console_subject_to_storage(subject: ConsoleSpaceSubject):
    if subject.subjectId is None or check_fake_id(subject.subjectId):
        subject.subjectId = get_surrogate_key()
    return storage_template.insert_one(subject, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def load_console_subject_list_by_ids(subject_id_list, current_user):
    return storage_template.find_(
        {"and": [{"subjectId": {"in": subject_id_list}}, {"tenantId": current_user.tenantId}]},
        ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def update_console_subject(console_subject: ConsoleSpaceSubject):

    return storage_template.update_one(console_subject, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def load_console_subject_by_id(subject_id, current_user) -> ConsoleSpaceSubject:
    return storage_template.find_one({"and": [{"subjectId": subject_id}, {"tenantId": current_user.tenantId}]},
                                     ConsoleSpaceSubject,
                                     CONSOLE_SPACE_SUBJECTS)


def delete_console_subject_by_id(subject_id):
    storage_template.delete_by_id(subject_id, CONSOLE_SPACE_SUBJECTS)


def delete_console_subject_by_ids(subject_ids):
    storage_template.delete_({"subjectId": {"in": subject_ids}}, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def rename_console_subject_by_id(subject_id, name):
    return storage_template.update_one_first({"subjectId": subject_id}, {"name": name}, ConsoleSpaceSubject,
                                             CONSOLE_SPACE_SUBJECTS)


def load_console_subject_by_report_id(report_id, current_user) -> ConsoleSpaceSubject:
    return storage_template.find_one({"reportIds": {"in": [report_id]}},
                                     ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def import_console_subject_to_db(subject):
    return storage_template.insert_one(subject, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)
