from storage.storage.storage_template import StorageTemplate

from watchmen.config.config import settings
from storage.storage.engine_adaptor import MONGO, MYSQL, ORACLE


def find_storage_template():
    if settings.STORAGE_ENGINE == MONGO:
        from watchmen.database.table.base_table_definition import TableDefinition
        return StorageTemplate(TableDefinition())
    elif settings.STORAGE_ENGINE == MYSQL:
        from watchmen.database.table.mysql_table_definition import MysqlTableDefinition
        return StorageTemplate(MysqlTableDefinition())
    elif settings.STORAGE_ENGINE == ORACLE:
        from watchmen.database.table import oracle_table_definition
        return StorageTemplate(oracle_table_definition)



