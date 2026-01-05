from fastapi import APIRouter, Request

from src.api.v1.dependencies.db import DBDep
from src.api.v1.responses.resourses import (
    CreateResourceResponse,
    DeleteResourceResponse,
    GetResourceResponse,
    GetResourcesResponse,
    GetStatusesResponse,
)
from src.schemas.resoures import ResourceAddDTO
from src.services.resources import ResourceService, ResourceStatusesService
from src.utils.exceptions import (
    ResourceAlreadyExistsError,
    ResourceAlreadyExistsHTTPError,
    ResourceNotFoundError,
    ResourceNotFoundHTTPError,
    ResourceUnavailableError,
    ResourceUnavailableHTTPError,
    ValueOutOfRangeError,
    ValueOutOfRangeHTTPError,
)

router = APIRouter(prefix="/resources")


@router.get("/")
async def get_resources(
    db: DBDep,
):
    resources = await ResourceService(db).get_resources()
    return GetResourcesResponse(
        data=resources,
    )


@router.post("/")
async def create_resource(
    request: Request,
    data: ResourceAddDTO,
    db: DBDep,
):
    try:
        resource = await ResourceService(db).create_resource(request=request, data=data)
    except ResourceUnavailableError as exc:
        raise ResourceUnavailableHTTPError from exc
    except ResourceAlreadyExistsError as exc:
        raise ResourceAlreadyExistsHTTPError from exc
    return CreateResourceResponse(
        data=resource,
    )


@router.get("/{resource_id}")
async def get_resource(
    resource_id: int,
    db: DBDep,
):
    try:
        resource = await ResourceService(db).get_resource(resource_id=resource_id)
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError from exc
    except ResourceNotFoundError as exc:
        raise ResourceNotFoundHTTPError from exc
    return GetResourceResponse(
        data=resource,
    )


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: int,
    db: DBDep,
):
    try:
        await ResourceService(db).delete_resource(resource_id=resource_id)
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError from exc
    except ResourceNotFoundError as exc:
        raise ResourceNotFoundHTTPError from exc
    return DeleteResourceResponse(
        detail="Resource was successfully deleted",
    )


@router.get("/{resource_id}/statuses")
async def get_statuses_by_resource(
    resource_id: int,
    db: DBDep,
):
    try:
        statuses = await ResourceStatusesService(db).get_statuses_by_resource(
            resource_id=resource_id
        )
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError from exc
    except ResourceNotFoundError as exc:
        raise ResourceNotFoundHTTPError from exc
    return GetStatusesResponse(
        data=statuses,
    )
