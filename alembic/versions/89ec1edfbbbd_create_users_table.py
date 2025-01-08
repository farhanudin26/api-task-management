"""create {users} table

Revision ID: 89ec1edfbbbd
Revises: 
Create Date: 2025-01-08 19:01:44.999657

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89ec1edfbbbd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
            sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
            sa.Column('username', sa.String(36), unique=True, nullable=False),
            sa.Column('name', sa.String(36), unique=True, nullable=False),
            sa.Column('email', sa.String(256),  unique=True, nullable=False),
            sa.Column('password', sa.String(512), unique=False, nullable=False),
            sa.Column('is_active', sa.Boolean, default=True),
            sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
            sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
            sa.Column('deleted_at', sa.DateTime, nullable=True),
    )

def downgrade() -> None:
    op.drop_table('users')
