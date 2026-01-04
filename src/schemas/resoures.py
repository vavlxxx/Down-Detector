from pydantic import HttpUrl, field_validator

from src.schemas.base import BaseDTO, TimingDTO


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
