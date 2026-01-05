# ruff: noqa: F401 F811
from httpx import AsyncClient

from src.schemas.resoures import ResourceDTO
from src.utils.exceptions import ResourceNotFoundHTTPError, ValueOutOfRangeHTTPError
from tests.integration.test_api.test_creating_resource import create_resource


async def test_get_multiple_resources(
    ac: AsyncClient,
    recreate_tables: None,
    create_resource: ResourceDTO,
) -> None:
    resp = await ac.get("/resources/")
    assert resp
    assert resp.status_code
    assert resp.status_code == 200

    data = resp.json()
    assert data
    assert data.get("data", False)
    assert len(data["data"]) == 1

    obj = ResourceDTO.model_validate(data["data"][0])

    assert obj == create_resource


async def test_get_single_resource(
    ac: AsyncClient,
    recreate_tables: None,
    create_resource: ResourceDTO,
) -> None:
    resp = await ac.get(f"/resources/{create_resource.resource_id}")
    assert resp
    assert resp.status_code
    assert resp.status_code == 200

    data = resp.json()
    assert data
    assert data.get("data", False)

    ResourceDTO.model_validate(data["data"])


async def test_get_non_existing_resource(
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


async def test_get_resource_with_invalid_id(
    ac: AsyncClient,
    recreate_tables: None,
    create_resource: ResourceDTO,
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
