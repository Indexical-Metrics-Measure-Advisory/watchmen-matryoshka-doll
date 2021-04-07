from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.storage.storage_template import insert_one, find_, update_one, find_by_id, delete_one, delete_, \
    find_one
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.console_space.model.console_space import ConsoleSpaceSubject

CONSOLE_SPACE_SUBJECTS = "console_space_subjects"

# template = find_template()


def create_console_subject_to_storage(subject: ConsoleSpaceSubject):
    if subject.subjectId is None or check_fake_id(subject.subjectId):
        subject.subjectId = get_surrogate_key()
    # return template.create(CONSOLE_SPACE_SUBJECTS, subject, ConsoleSpaceSubject)
    return insert_one(subject, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def load_console_subject_list_by_ids(subject_id_list):
    # return template.find(CONSOLE_SPACE_SUBJECTS, {"subjectId": {"$in": subject_id_list}}, ConsoleSpaceSubject)
    return find_({"subjectId": {"in": subject_id_list}}, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def update_console_subject(console_subject: ConsoleSpaceSubject):
    '''
    return template.update_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": console_subject.subjectId}, console_subject,
                               ConsoleSpaceSubject)
    '''
    return update_one(console_subject, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def load_console_subject_by_id(subject_id):
    # return template.find_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": subject_id}, ConsoleSpaceSubject)
    return find_by_id(subject_id, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def delete_console_subject_by_id(subject_id):
    # return template.delete_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": subject_id})
    delete_one(subject_id, CONSOLE_SPACE_SUBJECTS)


def delete_console_subject_by_ids(subject_ids):
    # return template.remove(CONSOLE_SPACE_SUBJECTS, {"subjectId": {"$in": subject_ids}})
    delete_({"subjectId": {"in": subject_ids}}, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def rename_console_subject_by_id(subject_id, name):
    # return template.update_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": subject_id}, {"name": name}, ConsoleSpaceSubject)
    return update_one({"subjectId": subject_id}, {"name": name}, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def load_console_subject_by_report_id(report_id):
    # return template.find_one(CONSOLE_SPACE_SUBJECTS, {"reportIds": {"$in": [report_id]}}, ConsoleSpaceSubject)
    return find_one({"reportIds": {"in": [report_id]}}, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)


def import_console_subject_to_db(subject):
    # return template.create(CONSOLE_SPACE_SUBJECTS, subject, ConsoleSpaceSubject)
    return insert_one(subject, ConsoleSpaceSubject, CONSOLE_SPACE_SUBJECTS)
