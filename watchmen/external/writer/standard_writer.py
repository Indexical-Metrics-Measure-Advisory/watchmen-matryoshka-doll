import json
import logging

import requests

from watchmen.common.utils.date_utils import DateTimeEncoder
from watchmen.external.model.external_writer import ExternalWriter
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)

def build_header(pat):
    headers = {"Content-Type": "application/json"}
    headers["authorization"] = "pat " + pat
    return headers


def init(external_writer: ExternalWriter, topic: Topic):
    async def write_to_standard(data):
        payload = {'code': topic.name, "data": data}
        response = requests.post(external_writer.url,timeout=1, data=json.dumps(payload, cls=DateTimeEncoder),
                                 headers=build_header(external_writer.pat))
        log.info(response.json())
        if response.status_code == 200:
            log.info(response.json())
        else:
            log.error(response.text)

    return write_to_standard
