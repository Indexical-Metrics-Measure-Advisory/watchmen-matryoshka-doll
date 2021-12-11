import requests

from watchmen.config.config import settings

session = requests.Session()
session.headers.update({"Content-Type": "application/json"})


def next_id():
    url = settings.SNOWFLAKE_REMOTE_HOST + "/snowflakeid"
    response = session.get(url)
    if response.status_code == 200:
        return response.text
