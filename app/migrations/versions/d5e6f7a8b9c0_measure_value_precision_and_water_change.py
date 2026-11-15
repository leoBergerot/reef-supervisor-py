"""Raise measure value precision; Water change requires %

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-11-15
"""

from typing import Sequence, Union

from alembic import op


revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Salinity density (e.g. 1.024) and fine phosphate readings need >2 decimals.
    op.execute(
        "ALTER TABLE measure ALTER COLUMN value TYPE NUMERIC(12, 4) USING value::numeric"
    )
    # Catalog unit is "%"; event-only (need_value=false) blocked percentage entry.
    op.execute(
        """
        UPDATE parameter
        SET need_value = true
        WHERE lower(name) = 'water change'
          AND is_custom = false
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE measure ALTER COLUMN value TYPE NUMERIC(10, 2) USING value::numeric"
    )
    op.execute(
        """
        UPDATE parameter
        SET need_value = false
        WHERE lower(name) = 'water change'
          AND is_custom = false
        """
    )
