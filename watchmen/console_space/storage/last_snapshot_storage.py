from model.model.console_space.last_snapshot import LastSnapshot

# from watchmen.database.storage.storage_template import insert_one, find_one, update_one
from watchmen.database.find_storage_template import find_storage_template

LAST_SNAPSHOT = "console_space_last_snapshot"

storage_template = find_storage_template()


# template = find_template()


def create_last_snapshot(last_snapshot):
    # return template.create(LAST_SNAPSHOT, last_snapshot, LastSnapshot)
    return storage_template.insert_one(last_snapshot, LastSnapshot, LAST_SNAPSHOT)


def save_last_snapshot(last_snapshot, current_user):
    result = load_last_snapshot(last_snapshot.userId, current_user)
    if result is not None:
        update_last_snapshot(last_snapshot.userId, last_snapshot)
    else:
        create_last_snapshot(last_snapshot)
    return last_snapshot


def load_last_snapshot(user_id, current_user) -> LastSnapshot:
    return storage_template.find_one({"and": [{"userId": user_id}, {"tenantId": current_user.tenantId}]}, LastSnapshot,
                                     LAST_SNAPSHOT)


def update_last_snapshot(user_id, last_snapshot):
    # return template.update_one(LAST_SNAPSHOT, {"userId": user_id}, last_snapshot, LastSnapshot)
    return storage_template.update_one(last_snapshot, LastSnapshot, LAST_SNAPSHOT)
