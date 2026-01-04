"""created basic models

Revision ID: fce0bc11d648
Revises:
Create Date: 2026-01-04 09:40:29.379306

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fce0bc11d648"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "resources",
        sa.Column("resource_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("resource_id", name=op.f("pk_resources")),
        sa.UniqueConstraint("url", name=op.f("uq_resources_url")),
    )
    op.create_table(
        "resourse_status",
        sa.Column(
            "resourse_status_id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("response_time", sa.Float(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["resource_id"],
            ["resources.resource_id"],
            name=op.f("fk_resourse_status_resource_id_resources"),
        ),
        sa.PrimaryKeyConstraint("resourse_status_id", name=op.f("pk_resourse_status")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("resourse_status")
    op.drop_table("resources")
