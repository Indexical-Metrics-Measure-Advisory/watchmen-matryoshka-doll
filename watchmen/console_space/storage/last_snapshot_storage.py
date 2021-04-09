from watchmen.common.storage.storage_template import insert_one, find_one, update_one
from watchmen.console_space.model.last_snapshot import LastSnapshot

LAST_SNAPSHOT = "console_space_last_snapshot"


# template = find_template()


def create_last_snapshot(last_snapshot):
    # return template.create(LAST_SNAPSHOT, last_snapshot, LastSnapshot)
    return insert_one(last_snapshot, LastSnapshot, LAST_SNAPSHOT)


def save_last_snapshot(last_snapshot):
    result = load_last_snapshot(last_snapshot.userId)
    if result is not None:
        update_last_snapshot(last_snapshot.userId, last_snapshot)
    else:
        create_last_snapshot(last_snapshot)
    return last_snapshot


def load_last_snapshot(user_id) -> LastSnapshot:
    # return template.find_one(LAST_SNAPSHOT, {"userId": user_id}, LastSnapshot)
    return find_one({"userId": user_id}, LastSnapshot, LAST_SNAPSHOT)


def update_last_snapshot(user_id, last_snapshot):
    # return template.update_one(LAST_SNAPSHOT, {"userId": user_id}, last_snapshot, LastSnapshot)
    return update_one({"userId": user_id}, last_snapshot, LastSnapshot, LAST_SNAPSHOT)
