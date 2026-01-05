# ruff: noqa: F401 F811
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from schemas.base import TimingDTO
from src.config import settings
from src.schemas.enums import ResourceState
from src.schemas.resoures import ResourceDTO, ResourceStatusAddDTO
from src.tasks.broker import broker
from src.tasks.dependencies import get_client
from src.tasks.schedule import check_resources, delete_unrelevant_statuses
from src.tasks.worker import check_single_resource
from src.utils.db_tools import DBManager
from tests.integration.test_api.test_creating_resource import create_resource, create_resource_bulk


@pytest.mark.anyio
async def test_taskiq_change_single_resource_state(
    recreate_tables: None,
    init_taskiq: None,
    create_resource: ResourceDTO,
    mock_aiohttp_success: AsyncMock,
    mock_aiohttp_timeout: AsyncMock,
    db: DBManager,
):
    await check_single_resource.kiq(  # type: ignore[call-arg]
        state=create_resource.state,
        resource_id=create_resource.resource_id,
        url=str(create_resource.url),
    )

    resource = await db.resources.get_one(resource_id=create_resource.resource_id)
    assert resource.state == ResourceState.UP

    statuses = await db.statuses.get_all_filtered(
        resource_id=create_resource.resource_id,
        status_code=200,
    )
    assert len(statuses) == 1

    async def mock_get_client():
        yield mock_aiohttp_timeout

    broker.dependency_overrides[get_client] = mock_get_client

    await check_single_resource.kiq(  # type: ignore[call-arg]
        state=create_resource.state,
        resource_id=create_resource.resource_id,
        url=str(create_resource.url),
    )

    resource = await db.resources.get_one(resource_id=create_resource.resource_id)
    assert resource.state == ResourceState.DOWN

    statuses = await db.statuses.get_all_filtered(
        resource_id=create_resource.resource_id,
        status_code=408,
    )
    assert len(statuses) == 1


@pytest.mark.anyio
async def test_taskiq_didnt_change_single_resource_state(
    recreate_tables: None,
    init_taskiq: None,
    create_resource: ResourceDTO,
    db: DBManager,
):
    await check_single_resource.kiq(  # type: ignore[call-arg]
        state=create_resource.state,
        resource_id=create_resource.resource_id,
        url=str(create_resource.url),
    )

    resource = await db.resources.get_one(resource_id=create_resource.resource_id)
    assert resource.state == ResourceState.UP

    await check_single_resource.kiq(  # type: ignore[call-arg]
        state=create_resource.state,
        resource_id=create_resource.resource_id,
        url=str(create_resource.url),
    )

    resource = await db.resources.get_one(resource_id=create_resource.resource_id)
    assert resource.state == ResourceState.UP


async def test_taskiq_change_multiple_resource_state(
    recreate_tables: None,
    init_taskiq: None,
    mock_aiohttp_timeout: AsyncMock,
    create_resource_bulk: list[ResourceDTO],
    db: DBManager,
):
    resources = await db.resources.get_all()
    assert resources
    assert len(resources) == len(create_resource_bulk)
    assert all([res.state == ResourceState.UP for res in resources])

    async def mock_get_client():
        yield mock_aiohttp_timeout

    broker.dependency_overrides[get_client] = mock_get_client
    await check_resources.kiq()  # type: ignore[call-arg]

    resources = await db.resources.get_all()
    assert resources
    assert len(resources) == len(create_resource_bulk)
    assert all([res.state == ResourceState.DOWN for res in resources])


async def test_taskiq_deletes_unrelevant_statuses(
    recreate_tables: None,
    init_taskiq: None,
    create_resource: ResourceDTO,
    db: DBManager,
):
    passed_datetime = datetime.now(timezone.utc) - timedelta(
        days=settings.taskiq.UNRELEVANT_STATUS_HOURS
    )
    obj = ResourceStatusAddDTO(
        resource_id=create_resource.resource_id, status_code=200, response_time=1
    )

    await db.statuses.add(obj)
    await db.commit()
    await db.statuses.edit(
        TimingDTO(
            created_at=passed_datetime,
            updated_at=passed_datetime,
        ),  # type: ignore
    )
    await db.commit()
    unrelevant_status = await db.statuses.get_one(resource_id=create_resource.resource_id)

    assert unrelevant_status
    assert unrelevant_status.created_at <= passed_datetime
    assert unrelevant_status.updated_at <= passed_datetime

    await delete_unrelevant_statuses.kiq()  # type: ignore[call-arg]

    status = await db.statuses.get_one_or_none(resource_id=create_resource.resource_id)
    assert status is None
