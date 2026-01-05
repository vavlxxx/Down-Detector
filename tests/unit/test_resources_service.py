# ruff: noqa: F401 F811
from unittest.mock import AsyncMock

import pytest

from src.schemas.resoures import ResourceDTO
from src.services.resources import ResourceService
from src.utils.db_tools import DBManager
from tests.integration.test_api.test_creating_resource import create_resource


async def test_raises_key_error_witout_supplied_state(
    recreate_tables: None,
    db: DBManager,
    create_resource: ResourceDTO,
    mock_aiohttp_success: AsyncMock,
):
    service = ResourceService(db)
    with pytest.raises(KeyError):
        await service.make_request_to_resource(
            resource_id=create_resource.resource_id,
            url=str(create_resource.url),
            client=mock_aiohttp_success,
        )
