import asyncio
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from watchmen.config.config import settings
from watchmen.connector.kafka import kafka_connector
from watchmen.connector.rabbitmq import rabbit_connector
from watchmen.monitor.prometheus.index import init_prometheus_monitor
from watchmen.routers import admin, console, common, auth, metadata, cache, pipeline

log = logging.getLogger("app." + __name__)

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.35",
              description="a lighter platform for data analytics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.PROMETHEUS_ON:
    init_prometheus_monitor(app)


@app.on_event("startup")
def startup():
    if settings.CONNECTOR_KAFKA:
        asyncio.create_task(kafka_connector.consume())
    elif settings.CONNECTOR_RABBITMQ:
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(rabbit_connector.consume(loop))


log.info("system init rest api")

app.include_router(admin.router)
app.include_router(console.router)
app.include_router(common.router)
app.include_router(auth.router)
app.include_router(metadata.router)
app.include_router(cache.router)
app.include_router(pipeline.router)
