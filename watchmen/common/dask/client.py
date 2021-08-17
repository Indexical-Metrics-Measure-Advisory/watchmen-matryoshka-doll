from distributed import Client

from watchmen.config.config import settings

client = Client(processes=settings.DASK_PROCESSES, dashboard_address=':0')


def get_dask_client():
    return client
