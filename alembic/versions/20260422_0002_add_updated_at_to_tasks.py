"""add updated_at to tasks

Revision ID: 20260422_0002
Revises: 20260302_0001
Create Date: 2026-04-22 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260422_0002"
down_revision = "20260302_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {col["name"] for col in inspector.get_columns("tasks")}
    if "updated_at" not in cols:
        with op.batch_alter_table("tasks") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "updated_at",
                    sa.DateTime(timezone=True),
                    nullable=False,
                    server_default=sa.text("CURRENT_TIMESTAMP"),
                )
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {col["name"] for col in inspector.get_columns("tasks")}
    if "updated_at" in cols:
        with op.batch_alter_table("tasks") as batch_op:
            batch_op.drop_column("updated_at")
