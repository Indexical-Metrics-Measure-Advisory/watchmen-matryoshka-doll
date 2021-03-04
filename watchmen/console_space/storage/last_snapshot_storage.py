from watchmen.common.storage.engine.storage_engine import get_client

db = get_client()
console_space_last_snapshot = db.get_collection('console_space_last_snapshot')


def create_last_snapshot(last_snapshot):
    console_space_last_snapshot.insert(last_snapshot.dict())


def save_last_snapshot(last_snapshot):
    result = load_last_snapshot(last_snapshot.userId)
    if result is not None:
        update_last_snapshot(last_snapshot.userId, last_snapshot)
    else:
        create_last_snapshot(last_snapshot)
    return last_snapshot


def load_last_snapshot(user_id):
    result = console_space_last_snapshot.find_one({"userId": user_id})
    if result is None:
        return None
    else:
        return result


def update_last_snapshot(user_id, last_snapshot):
    data = last_snapshot.dict()
    console_space_last_snapshot.update_one({"userId": user_id}, {"$set": data})
