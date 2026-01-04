import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import aiohttp

sys.path.append(str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api import router as main_router
from src.api.docs import router as docs_router
from src.config import settings
from src.db import engine

# from src.tasks.broker import broker, scheduler
from src.utils.db_tools import DBHealthChecker
from src.utils.logconfig import configurate_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger = get_logger("src")

    helper = DBHealthChecker(engine=engine)
    await helper.check()
    logger.info("All checks passed!")

    # if broker.is_worker_process:
    #     await scheduler.startup()
    #     await broker.startup()
    #     logger.info("Broker and scheduler started")

    async with aiohttp.ClientSession() as session:
        app.state.aiohttp_client = session
        yield

    # if broker.is_worker_process:
    #     await scheduler.shutdown()
    #     await broker.shutdown()
    #     logger.info("Broker and scheduler has been shut down")

    await helper.dispose()
    logger.info("Shutting down...")


configurate_logging()
app = FastAPI(
    title=settings.app.TITLE,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    default_response_class=ORJSONResponse,
)
app.include_router(main_router)
app.include_router(docs_router)


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=settings.uvicorn.UVICORN_HOST,
        port=settings.uvicorn.UVICORN_PORT,
        reload=settings.uvicorn.UVICORN_RELOAD,
        log_config="logging_config.json",
    )
