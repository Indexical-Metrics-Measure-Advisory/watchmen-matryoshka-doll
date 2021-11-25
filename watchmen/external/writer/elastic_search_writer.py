from model.model.external.external_writer import ExternalWriter


def init(external_writer: ExternalWriter):
    async def write_to_es(event_code: str, current_data, previous_data=None):
        raise NotImplementedError("not implemented")

    return write_to_es()
