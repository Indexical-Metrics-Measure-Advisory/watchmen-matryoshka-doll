import importlib

from watchmen.external.model.external_writer import ExternalWriter
from watchmen.topic.topic import Topic

WRITER_CORE_ACTION_ = "watchmen.external.writer."


def convert_writer_type(writer_type: str):
    return writer_type.replace("-", "_")


def get_writer_func(external_writer: ExternalWriter, topic: Topic):
    writer = importlib.import_module(WRITER_CORE_ACTION_ + convert_writer_type(external_writer.type))
    func = writer.init(external_writer, topic)
    return func
