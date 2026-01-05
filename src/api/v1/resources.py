from fastapi import APIRouter, Request

from src.api.v1.dependencies.db import DBDep
from src.api.v1.responses.resources import (
    RESP_CREATE_RESOURCE,
    RESP_DELETE_RESOURCE,
    RESP_GET_RESOURCE,
    RESP_GET_RESOURCE_STATUSES,
    RESP_GET_RESOURCES,
)
from src.schemas.resoures import ResourceAddDTO
from src.schemas.responses.resourses import (
    CreateResourceResponse,
    DeleteResourceResponse,
    GetResourceResponse,
    GetResourcesResponse,
    GetStatusesResponse,
)
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


@router.get(
    path="/",
    responses=RESP_GET_RESOURCES,
)
async def get_resources(
    db: DBDep,
):
    resources = await ResourceService(db).get_resources()
    return GetResourcesResponse(
        data=resources,
    )


@router.post(
    path="/",
    responses=RESP_CREATE_RESOURCE,
)
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


@router.get(
    path="/{resource_id}",
    responses=RESP_GET_RESOURCE,
)
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


@router.delete(
    path="/{resource_id}",
    responses=RESP_DELETE_RESOURCE,
)
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


@router.get(
    path="/{resource_id}/statuses",
    responses=RESP_GET_RESOURCE_STATUSES,
)
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
