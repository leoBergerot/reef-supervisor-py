"""Ensure Alkalinity (KH) is a numeric catalog parameter

Revision ID: c4d5e6f7a8b9
Revises: b2c3d4e5f6a7
Create Date: 2026-11-11
"""

from typing import Sequence, Union

from alembic import op


revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Local DBs (and some fixture loads) left Alkalinity.need_value=false, which
    # hides the numeric field in the dashboard create-measure form.
    op.execute(
        """
        UPDATE parameter
        SET need_value = true
        WHERE lower(name) = 'alkalinity'
          AND is_custom = false
        """
    )


def downgrade() -> None:
    pass
