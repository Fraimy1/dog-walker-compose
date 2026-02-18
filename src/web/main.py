import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.web.database import engine
from src.web.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Dog Walker Dashboard", lifespan=lifespan)
app.include_router(router)
