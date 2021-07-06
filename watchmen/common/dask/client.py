# import multiprocessing.popen_spawn_posix
from distributed import Client

from watchmen.config.config import settings

client = Client(processes=settings.DASK_PROCESSES)


def get_dask_client():
    return client
