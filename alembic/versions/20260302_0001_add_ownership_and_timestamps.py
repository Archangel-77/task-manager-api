"""create users and task ownership columns

Revision ID: 20260302_0001
Revises: 
Create Date: 2026-03-02 15:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260302_0001"
down_revision = None
branch_labels = None
depends_on = None


def _table_has_column(inspector, table_name: str, column_name: str) -> bool:
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("username", sa.String(), nullable=False),
            sa.Column("hashed_password", sa.String(), nullable=False),
        )
        op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
        op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    if not inspector.has_table("tasks"):
        op.create_table(
            "tasks",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("completed", sa.Boolean(), nullable=True, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        )
        op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)
        op.create_index(op.f("ix_tasks_owner_id"), "tasks", ["owner_id"], unique=False)
        return

    inspector = sa.inspect(bind)
    has_created_at = _table_has_column(inspector, "tasks", "created_at")
    has_owner_id = _table_has_column(inspector, "tasks", "owner_id")

    with op.batch_alter_table("tasks") as batch_op:
        if not has_created_at:
            batch_op.add_column(
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    nullable=False,
                    server_default=sa.text("CURRENT_TIMESTAMP"),
                )
            )
        if not has_owner_id:
            batch_op.add_column(sa.Column("owner_id", sa.Integer(), nullable=True))

    if not has_owner_id:
        existing_user = bind.execute(sa.text("SELECT id FROM users LIMIT 1")).first()
        if existing_user is None:
            bind.execute(
                sa.text(
                    "INSERT INTO users (username, hashed_password) VALUES (:username, :hashed_password)"
                ),
                {"username": "legacy_user", "hashed_password": "migration-placeholder"},
            )
            existing_user = bind.execute(sa.text("SELECT id FROM users LIMIT 1")).first()

        bind.execute(
            sa.text("UPDATE tasks SET owner_id = :owner_id WHERE owner_id IS NULL"),
            {"owner_id": existing_user[0]},
        )

        with op.batch_alter_table("tasks") as batch_op:
            batch_op.alter_column("owner_id", existing_type=sa.Integer(), nullable=False)
            batch_op.create_foreign_key("fk_tasks_owner_id_users", "users", ["owner_id"], ["id"], ondelete="CASCADE")
            batch_op.create_index(op.f("ix_tasks_owner_id"), ["owner_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("tasks"):
        with op.batch_alter_table("tasks") as batch_op:
            cols = {col["name"] for col in inspector.get_columns("tasks")}
            if "owner_id" in cols:
                try:
                    batch_op.drop_constraint("fk_tasks_owner_id_users", type_="foreignkey")
                except Exception:
                    pass
                try:
                    batch_op.drop_index(op.f("ix_tasks_owner_id"))
                except Exception:
                    pass
                batch_op.drop_column("owner_id")
            if "created_at" in cols:
                batch_op.drop_column("created_at")

    if inspector.has_table("users"):
        try:
            op.drop_index(op.f("ix_users_username"), table_name="users")
        except Exception:
            pass
        try:
            op.drop_index(op.f("ix_users_id"), table_name="users")
        except Exception:
            pass
        op.drop_table("users")
