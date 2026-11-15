"""account active flag and tank photo

Revision ID: c3a91e0b7d24
Revises: 0b441aca0794
Create Date: 2026-11-08 02:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3a91e0b7d24"
down_revision: Union[str, None] = "0b441aca0794"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("tank", sa.Column("photo_path", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("tank", "photo_path")
    op.drop_column("user", "is_active")
