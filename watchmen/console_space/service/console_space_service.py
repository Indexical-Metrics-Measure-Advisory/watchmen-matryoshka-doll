from watchmen.console_space.storage.console_space_storage import load_console_space_by_subject_id, save_console_space, \
    load_console_space_by_id, delete_console_space_storage
from watchmen.console_space.storage.console_subject_storage import delete_console_subject_by_id, \
    delete_console_subject_by_ids


def delete_console_subject(subject_id,current_user):
    delete_console_subject_by_id(subject_id)
    console_space = load_console_space_by_subject_id(subject_id,current_user)
    console_space.subjectIds.remove(subject_id)
    delete_console_subject_by_id(subject_id)
    save_console_space(console_space)


def delete_console_space_and_sub_data(connect_id,current_user):
    console_space = load_console_space_by_id(connect_id,current_user)
    if console_space.subjectIds:
        delete_console_subject_by_ids(console_space.subjectIds)
    # if console_space.groupIds:
    #     delete_console_group(console_space.groupIds)
    delete_console_space_storage(connect_id)
