from watchmen.external.model.external_writer import ExternalWriter


def init(external_writer:ExternalWriter):
    async def write_to_es(event_code,data):
        raise NotImplementedError("not implemented")

    return write_to_es()

