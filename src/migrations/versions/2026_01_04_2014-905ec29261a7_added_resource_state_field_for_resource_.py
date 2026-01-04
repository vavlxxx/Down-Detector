"""added resource state field for resource model

Revision ID: 905ec29261a7
Revises: fce0bc11d648
Create Date: 2026-01-04 20:14:58.815941

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "905ec29261a7"
down_revision: Union[str, Sequence[str], None] = "fce0bc11d648"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP TYPE IF EXISTS resource_state")
    resource_state_enum = postgresql.ENUM("UP", "DOWN", "UNKNOWN", name="resource_state")
    resource_state_enum.create(op.get_bind())

    op.add_column(
        "resource",
        sa.Column(
            "state",
            resource_state_enum,
            server_default="UP",
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("resource", "state")
    op.execute("DROP TYPE IF EXISTS resource_state")
