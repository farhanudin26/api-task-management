"""create {task_management} table

Revision ID: fbe374b56a33
Revises: 89ec1edfbbbd
Create Date: 2025-01-08 19:04:07.772799

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbe374b56a33'
down_revision: Union[str, None] = '89ec1edfbbbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'task_managements',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('task_management', sa.String(256), unique=False, nullable=True),
        sa.Column('description', sa.String(256), unique=False, nullable=True),
        sa.Column('date', sa.DateTime, nullable=False),
        sa.Column('priority', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
    )
    op.create_foreign_key("fk_task_managements_user_id", 'task_managements', 'users',
                        ["user_id"], ["id"], onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('task_managements')
