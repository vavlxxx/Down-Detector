from src.models.resoures import Resource, ResourceStatus
from src.repos.mappers.base import DataMapper
from src.schemas.resoures import ResourceDTO, ResourceStatusDTO


class ResourceMapper(DataMapper[Resource, ResourceDTO]):
    model = Resource
    schema = ResourceDTO


class ResourceStatusMapper(DataMapper[ResourceStatus, ResourceStatusDTO]):
    model = ResourceStatus
    schema = ResourceStatusDTO
