"""Corregir columna payment_method_id en tabla Pagos

Revision ID: 0ef4e96a3551
Revises: 5f58ad203fd6
Create Date: 2025-06-25 11:38:28.814467

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ef4e96a3551'
down_revision: Union[str, None] = '5f58ad203fd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("pagos", schema=None) as batch_op:
        batch_op.alter_column("payment_method",new_column_name="payment_method_id", type_=sa.Integer(), existing_type=sa.String())
        batch_op.create_foreign_key("fk_pagos_payment_method_id", 'metodosPago', ['payment_method_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("pagos", schema=None) as batch_op:
        batch_op.drop_constraint("fk_pagos_payment_method_id", type_='foreignkey')
        batch_op.alter_column("payment_method_id",new_column_name="payment_method", type_=sa.String(), existing_type=sa.Integer())

