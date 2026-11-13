from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.modules import routers

@asynccontextmanager
async def lifespan(app: FastAPI):

    yield

app = FastAPI(lifespan=lifespan)

app.include_router(routers)