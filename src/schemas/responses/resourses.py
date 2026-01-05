from src.schemas.base import BaseDTO
from src.schemas.resoures import ResourceDTO, ResourceStatusDTO


class GetResourcesResponse(BaseDTO):
    data: list[ResourceDTO]


class GetResourceResponse(BaseDTO):
    data: ResourceDTO


class CreateResourceResponse(BaseDTO):
    data: ResourceDTO


class DeleteResourceResponse(BaseDTO):
    detail: str


class GetStatusesResponse(BaseDTO):
    data: list[ResourceStatusDTO]
