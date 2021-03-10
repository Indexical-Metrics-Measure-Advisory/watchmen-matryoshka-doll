import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from watchmen.common.log import log
from watchmen.routers import admin, console, common, auth, metadata

log.init()

log = logging.getLogger("app." + __name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# h2o.init()

log.info("system init rest api")

app.include_router(admin.router)
app.include_router(console.router)
app.include_router(common.router)
app.include_router(auth.router)
app.include_router(metadata.router)
