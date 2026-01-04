from typing import Annotated

from taskiq import TaskiqDepends

from src.api.v1.dependencies.db import get_db
from src.services import resourses
from src.tasks.broker import broker
from src.utils.db_tools import DBManager


@broker.task(
    name="delete_unrelevant_statuses",
    schedule=[{"cron": "*/5 * * * *"}],
)
async def delete_unrelevant_statuses(
    db: Annotated[DBManager, TaskiqDepends(get_db)],
) -> None:
    await resourses.ResourceStatusesService(db).delete_unrelevant_statuses()


@broker.task(
    name="check_resources",
    schedule=[{"cron": "* * * * *"}],
)
async def check_resources(
    db: Annotated[DBManager, TaskiqDepends(get_db)],
) -> None:
    await resourses.ResourceService(db).check_resourses()
