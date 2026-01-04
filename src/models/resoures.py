from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.models.mixins.timing import TimingMixin
from src.schemas.enums import ResourceState


class Resource(Base, TimingMixin):
    __tablename__ = "resource"

    resource_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        sort_order=-1,
    )
    url: Mapped[str] = mapped_column(String(255), unique=True)
    state: Mapped[ResourceState] = mapped_column(
        ENUM(
            ResourceState,
            name="resource_state",
        ),
        default=ResourceState.UP,
    )


class ResourceStatus(Base, TimingMixin):
    __tablename__ = "resource_status"

    resource_status_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        sort_order=-1,
    )
    response_time: Mapped[float]
    status_code: Mapped[int]
    resource_id: Mapped[int] = mapped_column(ForeignKey(f"{Resource.__tablename__}.resource_id"))
