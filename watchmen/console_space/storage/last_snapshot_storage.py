from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.console_space.model.last_snapshot import LastSnapshot

LAST_SNAPSHOT = "console_space_last_snapshot"
#
# db = get_client()
# console_space_last_snapshot = db.get_collection('console_space_last_snapshot')


template = find_template()


def create_last_snapshot(last_snapshot):
    # console_space_last_snapshot.insert(last_snapshot.dict())
    return template.create(LAST_SNAPSHOT,last_snapshot,LastSnapshot)


def save_last_snapshot(last_snapshot):
    result = load_last_snapshot(last_snapshot.userId)
    if result is not None:
        update_last_snapshot(last_snapshot.userId, last_snapshot)
    else:
        create_last_snapshot(last_snapshot)
    return last_snapshot


def load_last_snapshot(user_id):
    # result = console_space_last_snapshot.find_one({"userId": user_id})
    # if result is None:
    #     return None
    # else:
    #     return result
    return  template.find_one(LAST_SNAPSHOT,{"userId": user_id},LastSnapshot)


def update_last_snapshot(user_id, last_snapshot):
    # data = last_snapshot.dict()
    # console_space_last_snapshot.update_one({"userId": user_id}, {"$set": data})
    return template.update_one(LAST_SNAPSHOT,{"userId": user_id},data)
