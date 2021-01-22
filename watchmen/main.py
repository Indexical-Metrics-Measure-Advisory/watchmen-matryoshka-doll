from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# import h2o

from watchmen.routers import admin, console, common, auth, monitor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# h2o.init()

app.include_router(admin.router)
app.include_router(console.router)
app.include_router(common.router)
app.include_router(auth.router)
app.include_router(monitor.router)
