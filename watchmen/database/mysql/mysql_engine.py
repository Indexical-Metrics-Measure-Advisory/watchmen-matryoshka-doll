import json

from sqlalchemy import create_engine

from watchmen.common.utils.date_utils import DateTimeEncoder
from watchmen.config.config import settings


def dumps(o):
    return json.dumps(o, cls=DateTimeEncoder)


"""
connection_url = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (settings.MYSQL_USER,
                                                          settings.MYSQL_PASSWORD,
                                                          settings.MYSQL_HOST,
                                                          settings.MYSQL_PORT,
                                                          settings.MYSQL_DATABASE)

engine = create_engine(connection_url,
                       echo=settings.MYSQL_ECHO,
                       future=True,
                       pool_recycle=3600,
                       json_serializer=dumps, encoding='utf-8')
"""