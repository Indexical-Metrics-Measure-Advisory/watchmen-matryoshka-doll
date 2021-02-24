from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.console_space.model.console_space import ConsoleSpaceSubject

db = get_client()
console_space_subject = db.get_collection('console_space_subject')


def create_console_subject_to_storage(subject: ConsoleSpaceSubject):
    if subject.subjectId is None or check_fake_id(subject.subjectId):
        subject.subjectId = get_surrogate_key()
    console_space_subject.insert_one(subject.dict())
    return ConsoleSpaceSubject.parse_obj(subject)


def load_console_subject_list_by_ids(subject_id_list):
    subject_list = console_space_subject.find({"subjectId": {"$in": subject_id_list}})
    return list(subject_list)


def update_console_subject(console_subject: ConsoleSpaceSubject):
    console_space_subject.update_one({"subjectId": console_subject.subjectId}, {"$set": console_subject.dict()})
    return ConsoleSpaceSubject.parse_obj(console_subject)


def load_console_subject_by_id(subject_id):
    result = console_space_subject.find_one({"subjectId": subject_id})
    return ConsoleSpaceSubject.parse_obj(result)


def delete_console_subject_by_id(subject_id):
    console_space_subject.delete_one({"subjectId": subject_id})


def delete_console_subject_by_ids(subject_ids):
    console_space_subject.remove({"subjectId": {"$in": subject_ids}})


def rename_console_subject_by_id(subject_id, name):
    console_space_subject.update_one({"subjectId": subject_id}, {"$set": {"name": name}})


def load_console_subject_by_report_id(report_id):
    result = console_space_subject.find_one({"reportIds": {"$in": [report_id]}})
    return ConsoleSpaceSubject.parse_obj(result)
