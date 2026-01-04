from src.models.resoures import Resource, ResourseStatus
from src.repos.mappers.base import DataMapper
from src.schemas.resoures import ResourceDTO, ResourseStatusDTO


class ResourceMapper(DataMapper[Resource, ResourceDTO]):
    model = Resource
    schema = ResourceDTO


class ResourseStatusMapper(DataMapper[ResourseStatus, ResourseStatusDTO]):
    model = ResourseStatus
    schema = ResourseStatusDTO
