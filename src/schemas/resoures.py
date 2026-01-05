from pydantic import HttpUrl, field_validator

from src.schemas.base import BaseDTO, TimingDTO
from src.schemas.enums import ResourceState


class ResourceAddDTO(BaseDTO):
    url: str

    @field_validator("url", mode="before")
    @classmethod
    def validate_url(cls, value: str) -> str:
        try:
            HttpUrl(value)
        except Exception as exc:
            raise ValueError("Invalid URL address") from exc
        return value


class ResourceUpdateDTO(BaseDTO):
    state: ResourceState | None = None


class ResourceDTO(ResourceAddDTO, TimingDTO):
    resource_id: int
    state: ResourceState

    @property
    def id(self) -> int:
        return self.resource_id


class ResourceStatusAddDTO(BaseDTO):
    resource_id: int
    response_time: float
    status_code: int


class ResourceStatusUpdateDTO(BaseDTO):
    status_code: int | None = None
    response_time: float | None = None


class ResourceStatusDTO(ResourceStatusAddDTO, TimingDTO):
    resource_status_id: int

    @property
    def id(self) -> int:
        return self.resource_status_id
