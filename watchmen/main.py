

from fastapi import FastAPI
from .routers import admin, console, common

app = FastAPI()


app.include_router(admin.router)
app.include_router(console.router)
app.include_router(common.router)


# TODO monitoring service

async def load_monitoring_data_by_pipeline_trace_id(pipeline_trace_id:str):
    pass

# TODO user cooperation API


## inbox

## notifications

## Timeline

## settings

# TODO  user session data
###
# pin and unpin
# position for available resources
# ##





## integration api

async def collection_data(template_space_name:str,instance_data:str,pipeline_name:str):
    pass

