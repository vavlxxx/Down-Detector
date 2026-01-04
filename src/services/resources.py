import asyncio
import time
from datetime import datetime, timedelta

import aiohttp
from fastapi import Request, status

from src.config import settings
from src.models.resoures import ResourceStatus
from src.schemas.enums import ResourceState
from src.schemas.resoures import (
    ResourceAddDTO,
    ResourceDTO,
    ResourceStatusAddDTO,
    ResourceStatusDTO,
    ResourceUpdateDTO,
)
from src.services.base import BaseService
from src.tasks import worker
from src.utils.exceptions import (
    ObjectNotFoundError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    ResourceUnavailableError,
)
from src.utils.logconfig import get_logger

logger = get_logger("resources")


class ResourceStatusesService(BaseService):
    async def get_statuses_by_resource(self, resource_id: int) -> list[ResourceStatusDTO]:
        await ResourceService(self.db).get_resource(resource_id=resource_id)
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
    def _is_valid_status(self, status_code: int) -> bool:
        anti_bot_protection = status_code == status.HTTP_403_FORBIDDEN
        success_status = status_code in range(status.HTTP_200_OK, status.HTTP_300_MULTIPLE_CHOICES)
        return success_status or anti_bot_protection

    async def create_resource(self, request: Request, data: ResourceAddDTO) -> ResourceDTO:
        created, resource = await self.db.resources.get_one_or_add(data=data)
        if not created:
            raise ResourceAlreadyExistsError

        response = await self.make_request_to_resource(
            url=str(data.url),
            resource_id=resource.id,
            client=request.app.state.aiohttp_client,
            save_to_db=False,
        )

        status_code = response.status_code
        if not self._is_valid_status(status_code):
            raise ResourceUnavailableError

        await self.db.commit()
        return resource

    async def get_resource(self, resource_id: int) -> ResourceDTO:
        try:
            return await self.db.resources.get_one(resource_id=resource_id)
        except ObjectNotFoundError as exc:
            raise ResourceNotFoundError from exc

    async def get_resources(self) -> list[ResourceDTO]:
        return await self.db.resources.get_all()

    async def delete_resource(self, resource_id: int):
        await self.db.statuses.delete(resource_id=resource_id, ensure_existence=False)
        try:
            await self.db.resources.delete(resource_id=resource_id)
        except ObjectNotFoundError as exc:
            raise ResourceNotFoundError from exc
        await self.db.commit()

    async def check_resources(self):
        resources = await self.db.resources.get_all()
        if not resources:
            logger.info("There is no resources to check. Skipping...")
            return

        tasks = []
        for resource in resources:
            tasks.append(
                worker.check_single_resource.kiq(
                    state=resource.state,
                    resource_id=resource.id,
                    url=str(resource.url),
                )  # type: ignore
            )
        await asyncio.gather(*tasks)

    async def toggle_resource_state(self, resource_id: int, state: ResourceState):
        states = (ResourceState.UP, ResourceState.DOWN)
        new_state_idx = int(state == ResourceState.UP)
        new_state = states[new_state_idx]

        update_obj = ResourceUpdateDTO(state=new_state)
        await self.db.resources.edit(
            resource_id=resource_id,
            data=update_obj,
            ensure_existence=False,
        )
        await self.db.commit()
        return new_state

    async def make_request_to_resource(
        self,
        url: str,
        resource_id: int,
        client: aiohttp.ClientSession,
        save_to_db: bool = True,
        *args,
        **kwargs,
    ) -> ResourceStatusAddDTO:
        start = time.perf_counter()
        status_code = status.HTTP_418_IM_A_TEAPOT

        try:
            async with client.get(url=url) as response:
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
            state: ResourceState = kwargs.get("state", None)
            if not state:
                logger.error("Cannot find required 'state' key in kwargs")
                raise KeyError("Missing 'state' key in kwargs")

            is_valid_status = self._is_valid_status(status_code)

            if (
                not is_valid_status
                and state == ResourceState.UP
                or is_valid_status
                and state == ResourceState.DOWN
            ):
                old_state = state
                new_state = await self.toggle_resource_state(
                    resource_id=resource_id,
                    state=state,
                )

                logger.info(
                    "Toggled %s resource state from %s to %s",
                    url,
                    old_state.value,
                    new_state.value,
                )

            await self.db.statuses.add(response)
            await self.db.commit()

        return response
