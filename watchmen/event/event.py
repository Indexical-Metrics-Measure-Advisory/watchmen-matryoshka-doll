# import datetime

from pydantic import BaseModel


class Event(BaseModel):
    type:str = None
    description:str = None
    # time: datetime = None


def before(func):
    def run_before():
        print("run_before")
        return func()

    return run_before


def after(func):
    def run_after(request):
        result = func(request)
        print ("run  event ",request)
        ## base on reuest type



        return result

    return run_after