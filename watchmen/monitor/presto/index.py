import requests

from watchmen.config.config import settings


def load_query_status_from_presto():
    url = settings.PRESTO_HTTP_URL + "/v1/query"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


