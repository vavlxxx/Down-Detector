from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from src.schemas.resoures import ResourceDTO, ResourceStatusAddDTO
from src.utils.exceptions import ResourceAlreadyExistsHTTPError, ResourceUnavailableHTTPError


@pytest.fixture(scope="function")
async def create_resource(ac_mocked: AsyncClient):
    resp = await ac_mocked.post("/resources/", json={"url": "https://example.com"})
    assert resp
    assert resp.status_code
    assert resp.status_code == 200
    data = resp.json()
    assert data
    assert data.get("data", False)
    assert data["data"]["url"] == "https://example.com"
    return ResourceDTO.model_validate(data["data"])


@pytest.fixture(scope="function")
async def create_resource_bulk(ac_mocked: AsyncClient):
    resp1 = await ac_mocked.post("/resources/", json={"url": "https://example1.com"})
    resp2 = await ac_mocked.post("/resources/", json={"url": "https://example2.com"})
    resp3 = await ac_mocked.post("/resources/", json={"url": "https://example3.com"})
    lst = (resp1, resp2, resp3)
    lst = tuple(map(lambda x: x.json(), lst))
    lst = tuple(map(lambda x: ResourceDTO.model_validate(x["data"]), lst))
    return lst


@pytest.mark.parametrize(
    "url, validation_error, expected_status, count",
    [
        ("https://www.google.com", False, 200, 1),
        ("https://www.example.com/nonexistent", False, 422, 1),
        ("https://github.com", False, 200, 2),
        ("http://invalid.website", False, 422, 2),
        ("https://stackoverflow.com", False, 200, 3),
        ("", True, 422, 3),
        ("https://www.python.org", False, 200, 4),
        ("134", True, 422, 4),
        ("https://docs.python.org", False, 200, 5),
        ("https://httpstat.us/500", False, 422, 5),
        ("https://www.wikipedia.org", False, 200, 6),
        ("http://localhost:9999", False, 422, 6),
        ("https://news.ycombinator.com", False, 200, 7),
        ("https://expired.badssl.com", False, 422, 7),
        ("https://www.reddit.com", False, 200, 8),
        ("https://self-signed.badssl.com", False, 422, 8),
        ("https://www.youtube.com", False, 200, 9),
        ("https://httpstat.us/403", False, 422, 9),
        ("https://www.amazon.com", False, 200, 10),
        ("https://wrong.host.badssl.com", False, 422, 10),
    ],
)
async def test_create_resource(
    url: str,
    expected_status: int,
    validation_error: bool,
    count: int,
    ac_mocked: AsyncClient,
    recreate_tables_module: None,
) -> None:
    mock_response = ResourceStatusAddDTO(
        resource_id=1,
        response_time=1.0,
        status_code=expected_status,
    )

    with patch(
        "src.services.resources.ResourceService.make_request_to_resource",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mocked_method:
        resp = await ac_mocked.post("/resources/", json={"url": url})

    assert resp
    assert resp.status_code
    assert resp.status_code == expected_status

    if not validation_error:
        mocked_method.assert_called_once()
    else:
        mocked_method.assert_not_called()

    resp = await ac_mocked.get("/resources/")
    assert resp
    assert resp.status_code
    assert resp.status_code == 200
    data = resp.json()
    assert data
    assert len(data["data"]) == count


async def test_conflict_during_creation(
    ac_mocked: AsyncClient,
    recreate_tables: None,
) -> None:
    resp = await ac_mocked.post("/resources/", json={"url": "https://example.com"})
    assert resp
    assert resp.status_code
    assert resp.status_code == 200

    resp = await ac_mocked.post("/resources/", json={"url": "https://example.com"})
    assert resp
    assert resp.status_code
    assert resp.status_code != 200

    data = resp.json()
    assert data
    assert data.get("detail", False)
    assert data["detail"] == ResourceAlreadyExistsHTTPError.detail
    assert resp.status_code == ResourceAlreadyExistsHTTPError.status


async def test_resource_unavailable(
    ac_mocked: AsyncClient,
    recreate_tables: None,
) -> None:
    mock_response = ResourceStatusAddDTO(
        resource_id=1,
        response_time=1.0,
        status_code=422,
    )

    with patch(
        "src.services.resources.ResourceService.make_request_to_resource",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as _:
        resp = await ac_mocked.post("/resources/", json={"url": "https://10.0.0.1"})

    assert resp
    assert resp.status_code
    assert resp.status_code != 200

    data = resp.json()
    assert data
    assert data.get("detail", False)
    assert data["detail"] == ResourceUnavailableHTTPError.detail
    assert resp.status_code == ResourceUnavailableHTTPError.status
