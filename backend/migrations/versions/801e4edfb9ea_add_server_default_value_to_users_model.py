"""add server default value to users model

Revision ID: 801e4edfb9ea
Revises: f1132bde4b8f
Create Date: 2026-11-18 21:43:02.172962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '801e4edfb9ea'
down_revision: Union[str, Sequence[str], None] = 'f1132bde4b8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'created_at', server_default=sa.text('now()'))
    op.alter_column('users', 'updated_at', server_default=sa.text('now()'))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'updated_at', server_default=None)
    op.alter_column('users', 'created_at', server_default=None)
