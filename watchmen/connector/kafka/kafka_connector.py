import asyncio
import json
import logging
import traceback

from aiokafka import AIOKafkaConsumer

from watchmen.collection.model.topic_event import TopicEvent
from watchmen.config.config import settings
from watchmen.raw_data.service.import_raw_data import import_raw_topic_data

log = logging.getLogger("app." + __name__)
loop = asyncio.get_event_loop()

kafka_topics = settings.KAFKA_TOPICS
kafka_topics_list = kafka_topics.split(",")


async def consume():
    consumer = AIOKafkaConsumer(
        kafka_topics_list,
        loop=loop, bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    await consumer.start()
    try:
        async for msg in consumer:
            topic_event = TopicEvent.parse_obj(msg.value)
            await import_raw_topic_data(topic_event)
    except:
        log.error(traceback.format_exc())
        await consume()
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()
