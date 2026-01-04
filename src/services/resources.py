import asyncio
import time
from datetime import datetime, timedelta

import aiohttp
from fastapi import status

from src.config import settings
from src.models.resoures import ResourceStatus
from src.schemas.resoures import ResourceAddDTO, ResourceDTO, ResourceStatusAddDTO, ResourceStatusDTO
from src.services.base import BaseService
from src.tasks import worker
from src.utils.exceptions import ResourceUnavailableError
from src.utils.logconfig import get_logger

logger = get_logger("resources")


class ResourceStatusesService(BaseService):
    async def get_statuses_by_resource(self, resource_id: int) -> list[ResourceStatusDTO]:
        return await self.db.statuses.get_all_filtered(resource_id=resource_id)

    async def delete_unrelevant_statuses(self):
        threshold = datetime.now() - timedelta(hours=settings.taskiq.UNRELEVANT_STATUS_HOURS)
        expression = ResourceStatus.created_at <= threshold
        statuses = await self.db.statuses.get_all_filtered(expression)
        if not statuses:
            logger.info(
                "There is no unrelevant statuses <= %s hours. Skipping...",
                settings.taskiq.UNRELEVANT_STATUS_HOURS,
            )
            return

        logger.debug("Found %s unrelevant statuses. Performing deletion", len(statuses))
        statuses_ids = tuple(st.id for st in statuses)
        await self.db.statuses.delete(ResourceStatus.resource_id.in_(statuses_ids))
        await self.db.commit()


class ResourceService(BaseService):
    async def create_resource(self, data: ResourceAddDTO) -> ResourceDTO:
        resource = await self.db.resources.get_one_or_add(data=data)
        response = await self.make_request_to_resource(str(data.url), resource.id, aiohttp.ClientSession())

        if response.status_code not in range(status.HTTP_200_OK, status.HTTP_300_MULTIPLE_CHOICES):
            raise ResourceUnavailableError

        await self.db.commit()
        return resource

    async def delete_resource(self, resource_id: int):
        await self.db.statuses.delete(resource_id=resource_id)
        await self.db.resources.delete(resource_id)
        await self.db.commit()

    async def check_resources(self):
        resources = await self.db.resources.get_all()
        if not resources:
            logger.info("There is no resources to check. Skipping...")
            return

        tasks = []
        for resource in resources:
            tasks.append(worker.check_single_resource.kiq(resource.id, str(resource.url)))  # type: ignore
        await asyncio.gather(*tasks)

    async def make_request_to_resource(
        self,
        url: str,
        resource_id: int,
        client: aiohttp.ClientSession,
        save_to_db: bool = True,
    ) -> ResourceStatusAddDTO:
        start = time.perf_counter()
        status_code = status.HTTP_418_IM_A_TEAPOT

        try:
            async with client.get(url) as response:
                status_code = response.status
                response.raise_for_status()
        except aiohttp.ClientResponseError as exc:
            logger.error("Exception during request to %s. Detail: %s", url, str(exc))
            status_code = exc.status
        except aiohttp.ClientConnectorError:
            logger.error("Cannot connect to %s", url)
            status_code = status.HTTP_408_REQUEST_TIMEOUT
        finally:
            end = time.perf_counter()
            response_time = end - start

        response = ResourceStatusAddDTO(
            resource_id=resource_id,
            response_time=response_time,
            status_code=status_code,
        )

        if save_to_db:
            await self.db.statuses.add(response)
            await self.db.commit()
        return response
