"""create {role} table

Revision ID: e0c9a62130d1
Revises: 506b619fc010
Create Date: 2025-01-10 15:02:06.627045

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0c9a62130d1'
down_revision: Union[str, None] = '506b619fc010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(36), unique=True, nullable=False),
        sa.Column('level', sa.Integer, nullable=False),
        sa.Column('name', sa.String(126), unique=True, nullable=False),
        sa.Column('description', sa.String(256), unique=False, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('roles')
