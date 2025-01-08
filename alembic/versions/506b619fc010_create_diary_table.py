"""create {diary} table

Revision ID: 506b619fc010
Revises: fbe374b56a33
Create Date: 2025-01-08 19:04:21.913665

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '506b619fc010'
down_revision: Union[str, None] = 'fbe374b56a33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'diarys',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('diary', sa.Text, nullable=False),
        sa.Column('date', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
    )
    op.create_foreign_key("fk_diarys_user_id", 'diarys', 'users',
                        ["user_id"], ["id"], onupdate='CASCADE')    


def downgrade() -> None:
    op.drop_table('diarys')
