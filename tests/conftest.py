# ruff: noqa: E402

from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock
from urllib.parse import urljoin

import aiohttp
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.v1.dependencies.db import get_db, get_db_with_null_pool
from src.config import settings
from src.db import engine_null_pool
from src.main import app
from src.models import *  # noqa: F403
from src.models.base import Base
from src.tasks.broker import broker
from src.tasks.dependencies import get_client
from src.utils.db_tools import DBHealthChecker, DBManager

app.dependency_overrides[get_db] = get_db_with_null_pool


@pytest.fixture()
async def db() -> AsyncGenerator[DBManager, None]:
    async for db in get_db_with_null_pool():
        yield db


@pytest.fixture(scope="module")
async def db_module() -> AsyncGenerator[DBManager, None]:
    async for db in get_db_with_null_pool():
        yield db


@pytest.fixture(scope="session", autouse=True)
async def check_test_mode() -> None:
    assert settings.app.MODE == "TEST"
    assert settings.db.DB_NAME == settings.db.DB_NAME_TEST


@pytest.fixture(scope="function")
async def recreate_tables(db: DBManager) -> None:
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="module")
async def recreate_tables_module(db_module: DBManager) -> None:
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def main(check_test_mode) -> None:
    await DBHealthChecker(engine=engine_null_pool).check()

    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function")
def mock_aiohttp_success():
    return _create_mock_client(200)


@pytest.fixture(scope="session")
def mock_aiohttp_success_session():
    return _create_mock_client(200)


@pytest.fixture(scope="function")
def mock_aiohttp_forbidden():
    return _create_mock_client(403)


@pytest.fixture(scope="function")
def mock_aiohttp_server_error():
    return _create_mock_client(500, raise_error=True)


@pytest.fixture(scope="function")
def mock_aiohttp_timeout():
    return _create_mock_client(408, raise_error=True)


def _create_mock_client(status: int, raise_error: bool = False):
    mock_response = AsyncMock()
    mock_response.status = status
    mock_response.raise_for_status = lambda: None

    if raise_error:
        mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
            request_info=AsyncMock(),
            history=(),
            status=status,
        )

    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_response
    mock_cm.__aexit__.return_value = AsyncMock()

    mock_client = AsyncMock(spec=aiohttp.ClientSession)
    mock_client.get.return_value = mock_cm

    return mock_client


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, Any]:
    app_ = ASGITransport(app=app)

    host = f"http://{settings.uvicorn.UVICORN_HOST}:{settings.uvicorn.UVICORN_PORT}"
    api_meta = f"{settings.app.API_PREFIX}{settings.app.V1_PREFIX}"
    url = urljoin(host, api_meta)

    async with AsyncClient(
        transport=app_,
        base_url=url,
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
async def ac_mocked(
    ac: AsyncClient,
    mock_aiohttp_success_session: AsyncMock,
) -> AsyncGenerator[AsyncClient, Any]:
    app.state.aiohttp_client = mock_aiohttp_success_session
    yield ac


@pytest.fixture(scope="function")
async def init_taskiq(
    mock_aiohttp_success: AsyncMock,
) -> AsyncGenerator[None, None]:
    async def mock_get_db():
        async for db in get_db_with_null_pool():
            yield db

    async def mock_get_client():
        yield mock_aiohttp_success

    broker.dependency_overrides[get_db] = mock_get_db
    broker.dependency_overrides[get_client] = mock_get_client

    yield
    broker.dependency_overrides.clear()
