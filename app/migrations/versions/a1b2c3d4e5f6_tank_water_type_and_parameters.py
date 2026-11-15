"""tank water_type, catalog flags, tank_parameter

Revision ID: a1b2c3d4e5f6
Revises: c3a91e0b7d24
Create Date: 2026-11-11 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "c3a91e0b7d24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tank",
        sa.Column("water_type", sa.String(), nullable=False, server_default="seawater"),
    )
    op.create_index(op.f("ix_tank_water_type"), "tank", ["water_type"], unique=False)

    op.add_column(
        "parameter",
        sa.Column("for_seawater", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "parameter",
        sa.Column("for_freshwater", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "parameter",
        sa.Column("is_custom", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "tank_parameter",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tank_id", sa.Integer(), nullable=False),
        sa.Column("parameter_id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tank_id"], ["tank.id"]),
        sa.ForeignKeyConstraint(["parameter_id"], ["parameter.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tank_id", "parameter_id", name="uq_tank_parameter_tank_parameter"),
    )
    op.create_index(op.f("ix_tank_parameter_tank_id"), "tank_parameter", ["tank_id"], unique=False)
    op.create_index(op.f("ix_tank_parameter_parameter_id"), "tank_parameter", ["parameter_id"], unique=False)

    # Align existing catalog rows with product defaults (match by name/sub_name).
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE parameter SET for_seawater = false, for_freshwater = true
            WHERE lower(name) = 'nitrite' OR lower(sub_name) IN ('no2', 'no₂')
            """
        )
    )
    connection.execute(
        sa.text(
            """
            UPDATE parameter SET for_seawater = true, for_freshwater = false
            WHERE lower(name) = 'calcium' OR lower(sub_name) IN ('ca', 'ca²⁺', 'ca2+')
            """
        )
    )

    now = sa.func.now()
    parameter = sa.table(
        "parameter",
        sa.column("name", sa.String()),
        sa.column("sub_name", sa.String()),
        sa.column("need_value", sa.Boolean()),
        sa.column("for_seawater", sa.Boolean()),
        sa.column("for_freshwater", sa.Boolean()),
        sa.column("is_custom", sa.Boolean()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )

    def ensure_parameter(name: str, sub_name: str, need_value: bool, for_seawater: bool, for_freshwater: bool) -> None:
        exists = connection.execute(
            sa.text(
                "SELECT id FROM parameter WHERE lower(name) = lower(:name) AND lower(sub_name) = lower(:sub_name) LIMIT 1"
            ),
            {"name": name, "sub_name": sub_name},
        ).first()
        if exists:
            connection.execute(
                sa.text(
                    """
                    UPDATE parameter
                    SET for_seawater = :for_seawater,
                        for_freshwater = :for_freshwater,
                        need_value = :need_value,
                        is_custom = false
                    WHERE id = :id
                    """
                ),
                {
                    "id": exists[0],
                    "for_seawater": for_seawater,
                    "for_freshwater": for_freshwater,
                    "need_value": need_value,
                },
            )
            return
        connection.execute(
            parameter.insert().values(
                name=name,
                sub_name=sub_name,
                need_value=need_value,
                for_seawater=for_seawater,
                for_freshwater=for_freshwater,
                is_custom=False,
                created_at=now,
                updated_at=now,
            )
        )

    ensure_parameter("Temperature", "°c", True, True, True)
    ensure_parameter("Alkalinity", "KH", True, True, True)
    ensure_parameter("Calcium", "CA", True, True, False)
    ensure_parameter("Magnesium", "Mg", True, True, False)
    ensure_parameter("Nitrate", "No3", True, True, True)
    ensure_parameter("Phosphate", "PO4", True, True, False)
    ensure_parameter("Salinity", "Density", True, True, False)
    ensure_parameter("Power of hydrogen", "pH", True, False, True)
    ensure_parameter("Nitrite", "No2", True, False, True)
    ensure_parameter("Water change", "%", False, False, True)

    # Seed tank_parameter for existing tanks from catalog defaults of their water_type.
    connection.execute(
        sa.text(
            """
            INSERT INTO tank_parameter (tank_id, parameter_id, enabled, created_at, updated_at)
            SELECT t.id, p.id, true, NOW(), NOW()
            FROM tank t
            JOIN parameter p ON p.is_custom = false
              AND (
                (t.water_type = 'seawater' AND p.for_seawater = true)
                OR (t.water_type = 'freshwater' AND p.for_freshwater = true)
              )
            ON CONFLICT DO NOTHING
            """
        )
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_tank_parameter_parameter_id"), table_name="tank_parameter")
    op.drop_index(op.f("ix_tank_parameter_tank_id"), table_name="tank_parameter")
    op.drop_table("tank_parameter")
    op.drop_column("parameter", "is_custom")
    op.drop_column("parameter", "for_freshwater")
    op.drop_column("parameter", "for_seawater")
    op.drop_index(op.f("ix_tank_water_type"), table_name="tank")
    op.drop_column("tank", "water_type")
