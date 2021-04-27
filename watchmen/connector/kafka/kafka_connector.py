import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from watchmen.collection.model.topic_event import TopicEvent
from watchmen.raw_data.service.import_raw_data import import_raw_topic_data

log = logging.getLogger("app." + __name__)
loop = asyncio.get_event_loop()

async def consume():
    consumer = AIOKafkaConsumer(
        'monitor_data',
        loop=loop, bootstrap_servers='localhost:9092',value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:

        async for msg in consumer:
            print(msg.value)
            topic_event = TopicEvent.parse_obj(msg.value)
            await import_raw_topic_data(topic_event)
    except:
        log.error("consumer error")
        await consume()
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

