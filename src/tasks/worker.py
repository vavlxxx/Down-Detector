from typing import Annotated

import aiohttp
from taskiq import TaskiqDepends

from src.api.v1.dependencies.db import get_db
from src.services import resources
from src.tasks.broker import broker
from src.tasks.dependencies import get_client
from src.utils.db_tools import DBManager


@broker.task(
    name="check_single_resource",
    retry_on_error=True,
    max_retries=3,
    delay=10,
)
async def check_single_resource(
    resource_id: int,
    url: str,
    client: Annotated[aiohttp.ClientSession, TaskiqDepends(get_client)],
    db: Annotated[DBManager, TaskiqDepends(get_db)],
) -> None:
    await resources.ResourceService(db).make_request_to_resource(
        url=url,
        client=client,
        resource_id=resource_id,
    )
