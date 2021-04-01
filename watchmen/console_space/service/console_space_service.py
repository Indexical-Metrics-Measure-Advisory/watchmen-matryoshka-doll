from watchmen.console_space.storage.console_space_storage import load_console_space_by_subject_id, save_console_space, \
    load_console_space_by_id, delete_console_space_storage
from watchmen.console_space.storage.console_subject_storage import delete_console_subject_by_id, \
    delete_console_subject_by_ids


def delete_console_subject(subject_id):
    delete_console_subject_by_id(subject_id)
    console_space = load_console_space_by_subject_id(subject_id)
    console_space.subjectIds.remove(subject_id)
    delete_console_subject_by_id(subject_id)
    save_console_space(console_space)


def delete_console_space_and_sub_data(connect_id):
    console_space = load_console_space_by_id(connect_id)
    if console_space.subjectIds:
        delete_console_subject_by_ids(console_space.subjectIds)
    # if console_space.groupIds:
    #     delete_console_group(console_space.groupIds)
    delete_console_space_storage(connect_id)

    # console_space.subjectIds

# def delete_console_group(group_ids):
#     group_list = load_console_group_list_by_ids(group_ids)
#     for group in group_list:
#         delete_console_subject_by_ids(group["subjectIds"])
