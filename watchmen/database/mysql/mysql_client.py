import json

from sqlalchemy import create_engine

from watchmen.common.utils.date_utils import DateTimeEncoder
from watchmen.database.datasource.data_source import DataSource





class MysqlEngine(object):
    engine = None

    def __init__(self, datasource: DataSource):
        connection_url = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (datasource.username,
                                                                  datasource.password,
                                                                  datasource.host,
                                                                  datasource.port,
                                                                  datasource.name)
        self.engine = create_engine(connection_url,
                                    echo=False,
                                    future=True,
                                    pool_recycle=3600,
                                    json_serializer=self.dumps, encoding='utf-8')

    def get_engine(self):
        return self.engine

    def dumps(o):
        return json.dumps(o, cls=DateTimeEncoder)
