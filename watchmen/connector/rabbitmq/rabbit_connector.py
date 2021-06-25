import asyncio
import json
import logging
import traceback


from watchmen.collection.model.topic_event import TopicEvent
from watchmen.config.config import settings
from watchmen.raw_data.service.import_raw_data import import_raw_topic_data

log = logging.getLogger("app." + __name__)



async def consume(loop):
    import aio_pika
    connection = await aio_pika.connect(
        settings.RABBITMQ_HOST, loop=loop
    )

    async with connection:
        queue_name = settings.RABBITMQ_QUEUE

        # Creating channel
        channel = await connection.channel()  # type: aio_pika.Channel

        # Declaring queue
        queue = await channel.declare_queue(
            queue_name,
            durable=settings.RABBITMQ_DURABLE,
            auto_delete=settings.RABBITMQ_AUTO_DELETE

        )  # type: aio_pika.Queue

        async with queue.iterator() as queue_iter:
            # Cancel consuming after __aexit__
            try:
                async for message in queue_iter:
                    async with message.process():
                        payload = json.loads(message.body)
                        topic_event = TopicEvent.parse_obj(payload)
                        await import_raw_topic_data(topic_event)
            except:
                log.error(traceback.format_exc())

