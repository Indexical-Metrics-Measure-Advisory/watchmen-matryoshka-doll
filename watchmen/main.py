import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from watchmen.config.config import settings
from watchmen.connector.kafka.kafka_connector import consume
from watchmen.routers import admin, console, common, auth, metadata

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


@app.on_event("startup")
def startup():
    if settings.CONNECTOR_KAFKA:
        asyncio.create_task(consume())


log.info("system init rest api")

app.include_router(admin.router)
app.include_router(console.router)
app.include_router(common.router)
app.include_router(auth.router)
app.include_router(metadata.router)
