from typing import List

from watchmen.database.storage import storage_template
from watchmen.external.model.external_writer import ExternalWriter

EXTERNAL_WRITER = "external_writer"


def create(external_writer: ExternalWriter) -> ExternalWriter:
    return storage_template.insert_one(external_writer, ExternalWriter, EXTERNAL_WRITER)


def update(external_writer: ExternalWriter) -> ExternalWriter:
    return storage_template.update_one(external_writer, ExternalWriter, EXTERNAL_WRITER)


def load_external_writers_with_page(query_name: str, pagination):
    if query_name != '':
        query_dict = {"writerCode": {"like": query_name}}
        sort_dict = [("lastModified", "desc")]
        return storage_template.page_(query_dict, sort_dict, pagination, ExternalWriter, EXTERNAL_WRITER)
    else:
        sort_dict = [("lastModified", "desc")]
    return storage_template.page_all(sort_dict, pagination, ExternalWriter, EXTERNAL_WRITER)


def load_external_writer_by_id(writer_id) -> ExternalWriter:
    return storage_template.find_one({"writerId": writer_id}, ExternalWriter, EXTERNAL_WRITER)


def load_external_writer_by_tenant_id(tenant_id: str) -> List[ExternalWriter]:
    return storage_template.find_({"tenantId": tenant_id}, ExternalWriter, EXTERNAL_WRITER)


