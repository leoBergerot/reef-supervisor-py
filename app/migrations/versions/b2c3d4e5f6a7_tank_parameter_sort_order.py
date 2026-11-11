"""tank_parameter.sort_order for dashboard reorder

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-11-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tank_parameter",
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                ROW_NUMBER() OVER (PARTITION BY tank_id ORDER BY id) - 1 AS rn
            FROM tank_parameter
        )
        UPDATE tank_parameter AS tp
        SET sort_order = ranked.rn
        FROM ranked
        WHERE tp.id = ranked.id
        """
    )


def downgrade() -> None:
    op.drop_column("tank_parameter", "sort_order")
