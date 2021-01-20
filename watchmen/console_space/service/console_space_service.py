from watchmen.console_space.storage.console_space_storage import load_console_space_by_subject_id, save_console_space
from watchmen.console_space.storage.console_subject_storage import delete_console_subject_by_id


def delete_console_subject(subject_id):
    delete_console_subject_by_id(subject_id)
    console_space =load_console_space_by_subject_id(subject_id)
    console_space.subjectIds.remove(subject_id)
    save_console_space(console_space)
