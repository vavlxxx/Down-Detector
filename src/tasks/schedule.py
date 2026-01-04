from typing import Annotated

from taskiq import TaskiqDepends

from src.api.v1.dependencies.db import get_db
from src.config import settings
from src.services import resources
from src.tasks.broker import broker
from src.utils.db_tools import DBManager


@broker.task(
    name="delete_unrelevant_statuses",
    schedule=[{"cron": settings.taskiq.CRON_CHECK_UNRELEVANT_STATUSES}],
)
async def delete_unrelevant_statuses(
    db: Annotated[DBManager, TaskiqDepends(get_db)],
) -> None:
    await resources.ResourceStatusesService(db).delete_unrelevant_statuses()


@broker.task(
    name="check_resources",
    schedule=[{"cron": settings.taskiq.CRON_CHECK_RESOURCES}],
)
async def check_resources(
    db: Annotated[DBManager, TaskiqDepends(get_db)],
) -> None:
    await resources.ResourceService(db).check_resources()
