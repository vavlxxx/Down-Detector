# ruff: noqa: F401 F811
from unittest.mock import AsyncMock

from httpx import AsyncClient

from src.schemas.resoures import ResourceDTO, ResourceStatusDTO
from src.tasks.broker import broker
from src.tasks.dependencies import get_client
from src.tasks.schedule import check_resources
from src.utils.exceptions import ResourceNotFoundHTTPError, ValueOutOfRangeHTTPError
from tests.integration.test_api.test_creating_resource import create_resource


async def test_get_statuses(
    ac: AsyncClient,
    recreate_tables: None,
    init_taskiq: None,
    mock_aiohttp_timeout: AsyncMock,
    create_resource: ResourceDTO,
) -> None:
    await check_resources.kiq()  # type: ignore[call-arg]
    resource_id = create_resource.resource_id
    resp = await ac.get(f"/resources/{resource_id}/statuses")
    assert resp
    assert resp.status_code
    assert resp.status_code == 200

    data = resp.json()
    assert data
    assert data.get("data", False)
    assert len(data["data"]) == 1

    lst = data["data"]
    assert all([ResourceStatusDTO.model_validate(st) for st in lst])

    async def mock_get_client():
        yield mock_aiohttp_timeout

    broker.dependency_overrides[get_client] = mock_get_client
    await check_resources.kiq()  # type: ignore[call-arg]

    resp = await ac.get(f"/resources/{resource_id}/statuses")
    assert resp
    assert resp.status_code
    assert resp.status_code == 200

    data = resp.json()
    assert data
    assert data.get("data", False)
    assert len(data["data"]) == 2

    lst = data["data"]
    assert all([ResourceStatusDTO.model_validate(st) for st in lst])


async def test_get_statuses_by_non_existing_resource(
    ac: AsyncClient,
    recreate_tables: None,
    create_resource: ResourceDTO,
) -> None:
    not_existing_id = create_resource.resource_id + 1
    resp = await ac.get(f"/resources/{not_existing_id}")
    assert resp
    assert resp.status_code
    assert resp.status_code != 200

    data = resp.json()
    assert data
    assert data.get("detail", False)
    assert data["detail"] == ResourceNotFoundHTTPError.detail
    assert resp.status_code == ResourceNotFoundHTTPError.status


async def test_get_statuses_by_resource_with_invalid_id(
    ac: AsyncClient,
    recreate_tables: None,
    create_resource: int,
) -> None:
    invalid_id = 2**32
    resp = await ac.get(f"/resources/{invalid_id}")
    assert resp
    assert resp.status_code
    assert resp.status_code != 200

    data = resp.json()
    assert data
    assert data.get("detail", False)
    assert data["detail"] == ValueOutOfRangeHTTPError.detail
    assert resp.status_code == ValueOutOfRangeHTTPError.status
