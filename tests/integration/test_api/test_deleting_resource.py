# ruff: noqa: F401 F811
from httpx import AsyncClient

from src.schemas.resoures import ResourceDTO
from src.utils.exceptions import ResourceNotFoundHTTPError, ValueOutOfRangeHTTPError
from tests.integration.test_api.test_creating_resource import create_resource


async def test_delete_resource(
    ac: AsyncClient,
    recreate_tables: None,
    create_resource: ResourceDTO,
) -> None:
    resp = await ac.delete(f"/resources/{create_resource.resource_id}")
    assert resp
    assert resp.status_code
    assert resp.status_code == 200

    data = resp.json()
    assert data
    assert data.get("detail", False)


async def test_delete_non_existing_resource(
    ac: AsyncClient,
    recreate_tables: None,
    create_resource: ResourceDTO,
) -> None:
    not_existing_id = create_resource.resource_id + 1
    resp = await ac.delete(f"/resources/{not_existing_id}")
    assert resp
    assert resp.status_code
    assert resp.status_code != 200
    assert resp.status_code == ResourceNotFoundHTTPError.status

    data = resp.json()
    assert data
    assert data.get("detail", False)
    assert data["detail"] == ResourceNotFoundHTTPError.detail


async def test_delete_resource_with_invalid_id(
    ac: AsyncClient,
    recreate_tables: None,
    create_resource: ResourceDTO,
) -> None:
    invalid_id = 2**32
    resp = await ac.delete(f"/resources/{invalid_id}")
    assert resp
    assert resp.status_code
    assert resp.status_code != 200
    assert resp.status_code == ValueOutOfRangeHTTPError.status

    data = resp.json()
    assert data
    assert data.get("detail", False)
    print(data["detail"])
    assert data["detail"] == ValueOutOfRangeHTTPError.detail
