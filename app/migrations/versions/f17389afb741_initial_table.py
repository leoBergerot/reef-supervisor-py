"""Initial table

Revision ID: f17389afb741
Revises: 
Create Date: 2025-01-02 13:27:20.459326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f17389afb741'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('parameter',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('sub_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('need_value', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parameter_name'), 'parameter', ['name'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('tank',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tank_name'), 'tank', ['name'], unique=False)
    op.create_index(op.f('ix_tank_user_id'), 'tank', ['user_id'], unique=False)
    op.create_table('measure',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parameter_id', sa.Integer(), nullable=False),
    sa.Column('tank_id', sa.Integer(), nullable=False),
    sa.Column('value', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['parameter_id'], ['parameter.id'], ),
    sa.ForeignKeyConstraint(['tank_id'], ['tank.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_measure_parameter_id'), 'measure', ['parameter_id'], unique=False)
    op.create_index(op.f('ix_measure_tank_id'), 'measure', ['tank_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_measure_tank_id'), table_name='measure')
    op.drop_index(op.f('ix_measure_parameter_id'), table_name='measure')
    op.drop_table('measure')
    op.drop_index(op.f('ix_tank_user_id'), table_name='tank')
    op.drop_index(op.f('ix_tank_name'), table_name='tank')
    op.drop_table('tank')
    op.drop_table('user')
    op.drop_index(op.f('ix_parameter_name'), table_name='parameter')
    op.drop_table('parameter')
    # ### end Alembic commands ###
