from src.models.resoures import Resource, ResourceStatus
from src.repos.base import BaseRepo
from src.repos.mappers.mappers import ResourceMapper, ResourceStatusMapper
from src.schemas.resoures import (
    ResourceDTO,
    ResourceStatusDTO,
    ResourceStatusUpdateDTO,
    ResourceUpdateDTO,
)


class ResourceRepo(BaseRepo[Resource, ResourceDTO, ResourceUpdateDTO]):
    schema = ResourceDTO
    mapper = ResourceMapper
    model = Resource


class ResourceStatusRepo(BaseRepo[ResourceStatus, ResourceStatusDTO, ResourceStatusUpdateDTO]):
    schema = ResourceStatusDTO
    mapper = ResourceStatusMapper
    model = ResourceStatus
