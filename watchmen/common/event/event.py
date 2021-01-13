from watchmen.common.mongo_model import MongoModel


class Event(MongoModel):
    type: str = None
    description: str = None
    # time: datetime = None


def before(func):
    def run_before():
        print("run_before")
        return func()

    return run_before


