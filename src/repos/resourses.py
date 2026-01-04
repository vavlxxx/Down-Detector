from src.models.resoures import Resource, ResourseStatus
from src.repos.base import BaseRepo
from src.repos.mappers.mappers import ResourceMapper, ResourseStatusMapper
from src.schemas.resoures import ResourceDTO, ResourseStatusDTO


class ResourceRepo(BaseRepo[Resource, ResourceDTO]):
    schema = ResourceDTO
    mapper = ResourceMapper
    model = Resource


class ResourseStatusRepo(BaseRepo[ResourseStatus, ResourseStatusDTO]):
    schema = ResourseStatusDTO
    mapper = ResourseStatusMapper
    model = ResourseStatus
