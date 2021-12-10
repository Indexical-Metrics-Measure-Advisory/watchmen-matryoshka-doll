import dask
from distributed import Client

from watchmen.config.config import settings

client = Client(processes=settings.DASK_PROCESSES, dashboard_address=':0')

if settings.DASK_TEMP:
    dask.config.set(temporary_directory=settings.DASK_TEMP)


def get_dask_client():
    return client
