from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.models.mixins.primary_key import PrimaryKeyMixin
from src.models.mixins.timing import TimingMixin


class Resource(Base, PrimaryKeyMixin, TimingMixin):
    __tablename__ = "resources"
    _pk_column_name = "resource_id"

    url: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)


class ResourseStatus(Base, PrimaryKeyMixin, TimingMixin):
    __tablename__ = "resourse_status"
    _pk_column_name = "resourse_status_id"

    response_time: Mapped[float]
    status_code: Mapped[int]
    resource_id: Mapped[int] = mapped_column(
        ForeignKey(f"{Resource.__tablename__}.{Resource._pk_column_name}")
    )
