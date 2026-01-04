from pydantic import HttpUrl

from src.schemas.base import BaseDTO, TimingDTO


class ResourceAddDTO(BaseDTO):
    url: HttpUrl


class ResourceDTO(ResourceAddDTO, TimingDTO):
    resource_id: int

    @property
    def id(self) -> int:
        return self.resource_id


class ResourceStatusAddDTO(BaseDTO):
    resource_id: int
    response_time: float
    status_code: int


class ResourceStatusDTO(ResourceStatusAddDTO, TimingDTO):
    resource_status_id: int

    @property
    def id(self) -> int:
        return self.resource_status_id
