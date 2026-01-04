from pydantic import HttpUrl

from src.schemas.base import BaseDTO, TimingDTO


class ResourceAddDTO(BaseDTO):
    url: HttpUrl


class ResourceDTO(ResourceAddDTO, TimingDTO):
    resource_id: int

    @property
    def id(self) -> int:
        return self.resource_id


class ResourseStatusAddDTO(BaseDTO):
    resource_id: int
    response_time: float
    status_code: int


class ResourseStatusDTO(ResourseStatusAddDTO, TimingDTO):
    resourse_status_id: int

    @property
    def id(self) -> int:
        return self.resourse_status_id
