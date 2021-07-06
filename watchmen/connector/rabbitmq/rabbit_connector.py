import json
import logging
import traceback

from aio_pika import ExchangeType

from watchmen.auth.storage.user import get_user, load_user_by_name
from watchmen.collection.model.topic_event import TopicEvent
from watchmen.config.config import settings
from watchmen.raw_data.service.import_raw_data import import_raw_topic_data

log = logging.getLogger("app." + __name__)


async def consume(loop):
    import aio_pika
    connection = await aio_pika.connect(
        host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, loop=loop, virtualhost=settings.RABBITMQ_VIRTUALHOST,
        login=settings.RABBITMQ_USERNAME
        , password=settings.RABBITMQ_PASSWORD
    )

    async with connection:
        queue_name = settings.RABBITMQ_QUEUE

        channel = await connection.channel()

        queue = await channel.declare_queue(
            queue_name,
            durable=settings.RABBITMQ_DURABLE,
            auto_delete=settings.RABBITMQ_AUTO_DELETE

        )
        exchange = await channel.declare_exchange(name=queue_name, type=ExchangeType.DIRECT, auto_delete=True)

        await queue.bind(exchange, queue_name)
        # Creating channel

        async with queue.iterator() as queue_iter:
            # Cancel consuming after __aexit__
            try:
                async for message in queue_iter:
                    async with message.process():
                        payload = json.loads(message.body)
                        topic_event = TopicEvent.parse_obj(payload)
                        user = load_user_by_name(settings.MOCK_USER)
                        await import_raw_topic_data(topic_event,user)
            except:
                log.error(traceback.format_exc())
