from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import status

from src.schemas.enums import ResourceState
from src.schemas.resoures import ResourceDTO, ResourceStatusDTO
from src.schemas.responses.resourses import (
    CreateResourceResponse,
    DeleteResourceResponse,
    GetResourceResponse,
    GetResourcesResponse,
    GetStatusesResponse,
)
from src.utils.exceptions import (
    ResourceAlreadyExistsHTTPError,
    ResourceNotFoundHTTPError,
    ResourceUnavailableHTTPError,
    ValueOutOfRangeHTTPError,
)

RESP_GET_RESOURCES: Dict[int | str, Dict[str, Any]] | None = {
    status.HTTP_200_OK: {
        "description": "Ресурсы успешно полуяены",
        "model": GetResourcesResponse,
        "example": GetResourcesResponse(
            data=[
                ResourceDTO(
                    resource_id=1,
                    url="https://example.com",
                    state=ResourceState.UP,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            ]
        ),
    },
}

RESP_GET_RESOURCE: Dict[int | str, Dict[str, Any]] | None = {
    status.HTTP_200_OK: {
        "description": "Ресурс успешно полуяен",
        "model": GetResourceResponse,
        "example": GetResourceResponse(
            data=ResourceDTO(
                resource_id=1,
                url="https://example.com",
                state=ResourceState.UP,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        ),
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Ресурс не найден",
        "content": {"application/json": {"example": {"detail": ResourceNotFoundHTTPError.detail}}},
    },
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "description": "Некорректные данные для id ресурса",
        "content": {"application/json": {"example": {"detail": ValueOutOfRangeHTTPError.detail}}},
    },
}

RESP_DELETE_RESOURCE: Dict[int | str, Dict[str, Any]] | None = {
    status.HTTP_200_OK: {
        "description": "Ресурс успешно полуяен",
        "model": DeleteResourceResponse,
        "example": DeleteResourceResponse(
            detail="Resource was successfully deleted",
        ),
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Ресурс не найден",
        "content": {"application/json": {"example": {"detail": ResourceNotFoundHTTPError.detail}}},
    },
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "description": "Некорректные данные для id ресурса",
        "content": {"application/json": {"example": {"detail": ValueOutOfRangeHTTPError.detail}}},
    },
}

RESP_CREATE_RESOURCE: Dict[int | str, Dict[str, Any]] | None = {
    status.HTTP_200_OK: {
        "description": "Ресурс успешно создан",
        "model": CreateResourceResponse,
        "example": CreateResourceResponse(
            data=ResourceDTO(
                resource_id=1,
                url="https://example.com",
                state=ResourceState.UP,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        ),
    },
    status.HTTP_409_CONFLICT: {
        "description": "Ресурс с таким URL уже существует",
        "content": {
            "application/json": {"example": {"detail": ResourceAlreadyExistsHTTPError.detail}}
        },
    },
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "description": "Не удалось получить информацию о ресурсе",
        "content": {
            "application/json": {"example": {"detail": ResourceUnavailableHTTPError.detail}}
        },
    },
}

RESP_GET_RESOURCE_STATUSES: Dict[int | str, Dict[str, Any]] | None = {
    status.HTTP_200_OK: {
        "description": "Статусы для ресурсов успешно получены",
        "model": GetResourcesResponse,
        "example": GetStatusesResponse(
            data=[
                ResourceStatusDTO(
                    resource_status_id=1,
                    resource_id=1,
                    status_code=200,
                    response_time=0.6503,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            ]
        ),
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Ресурс не найден",
        "content": {"application/json": {"example": {"detail": ResourceNotFoundHTTPError.detail}}},
    },
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "description": "Некорректные данные для id ресурса",
        "content": {"application/json": {"example": {"detail": ValueOutOfRangeHTTPError.detail}}},
    },
}
