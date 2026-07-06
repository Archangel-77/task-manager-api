"""Add name field to User model

Revision ID: aa1c81867a95
Revises: 20260422_0002
Create Date: 2026-07-06 15:15:05.120261
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa1c81867a95'
down_revision = '20260422_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('name', sa.String(length=100), nullable=False))

def downgrade() -> None:
    op.drop_column('users', 'name')
