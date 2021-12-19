import dask
from dask.distributed import Client

from watchmen_boot.config.config import settings
from watchmen_boot.utils.singleton import singleton

if settings.DASK_TEMP:
    dask.config.set(temporary_directory=settings.DASK_TEMP)


@singleton
class DaskClient:

    def __init__(self):
        self.client = Client(processes=settings.DASK_PROCESSES)

    def get_dask_client(self):
        return self.client
