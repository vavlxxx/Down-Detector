from pydantic import HttpUrl

from src.schemas.base import BaseDTO, TimingDTO


class ResourceAddDTO(BaseDTO):
    url: HttpUrl


class ResourceDTO(ResourceAddDTO, TimingDTO):
    resource_id: int


class ResourseStatusAddDTO(BaseDTO):
    response_time: float
    status_code: int
    resource_id: int


class ResourseStatusDTO(ResourseStatusAddDTO, TimingDTO):
    resourse_status_id: int
