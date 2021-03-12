from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.console_space.model.console_space import ConsoleSpaceSubject

CONSOLE_SPACE_SUBJECTS = "console_space_subjects"

# db = get_client()
# console_space_subjects = db.get_collection('console_space_subjects')

template = find_template()


def create_console_subject_to_storage(subject: ConsoleSpaceSubject):
    if subject.subjectId is None or check_fake_id(subject.subjectId):
        subject.subjectId = get_surrogate_key()
    return template.create(CONSOLE_SPACE_SUBJECTS, subject, ConsoleSpaceSubject)
    # console_space_subjects.insert_one(subject.dict())
    # return ConsoleSpaceSubject.parse_obj(subject)


def load_console_subject_list_by_ids(subject_id_list):
    # subject_list = console_space_subjects.find({"subjectId": {"$in": subject_id_list}})
    # return list(subject_list)
    return template.find(CONSOLE_SPACE_SUBJECTS, {"subjectId": {"$in": subject_id_list}}, ConsoleSpaceSubject)


def update_console_subject(console_subject: ConsoleSpaceSubject):
    # console_space_subjects.update_one({"subjectId": console_subject.subjectId}, {"$set": console_subject.dict()})
    # return ConsoleSpaceSubject.parse_obj(console_subject)
    return template.update_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": console_subject.subjectId}, console_subject,
                               ConsoleSpaceSubject)


def load_console_subject_by_id(subject_id):
    # result = console_space_subjects.find_one({"subjectId": subject_id})
    # if result is None:
    #     return None
    # else:
    #     return ConsoleSpaceSubject.parse_obj(result)
    return template.find_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": subject_id}, ConsoleSpaceSubject)


def delete_console_subject_by_id(subject_id):
    # console_space_subjects.delete_one({"subjectId": subject_id})
    return template.delete_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": subject_id})


def delete_console_subject_by_ids(subject_ids):
    # console_space_subjects.remove({"subjectId": {"$in": subject_ids}})
    return template.remove(CONSOLE_SPACE_SUBJECTS, {"subjectId": {"$in": subject_ids}})


def rename_console_subject_by_id(subject_id, name):
    # console_space_subjects.update_one({"subjectId": subject_id}, {"$set": {"name": name}})
    return template.update_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": subject_id}, {"name": name})


def load_console_subject_by_report_id(report_id):
    # result = console_space_subjects.find_one({"reportIds": {"$in": [report_id]}})
    # return ConsoleSpaceSubject.parse_obj(result)
    return template.find_one(CONSOLE_SPACE_SUBJECTS, {"reportIds": {"$in": [report_id]}}, ConsoleSpaceSubject)


def import_console_subject_to_db(subject):
    # console_space_subjects.insert_one(subject)
    return template.create(CONSOLE_SPACE_SUBJECTS, subject, ConsoleSpaceSubject)
