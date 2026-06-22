"""create tasks table

Revision ID: 8b224eb85e99
Revises: 
Create Date: 2026-06-23 23:07:37.522668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = '8b224eb85e99'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


task_priority = postgresql.ENUM("LOW", "MEDIUM", "HIGH", name="task_priority", create_type=False)
task_status = postgresql.ENUM(
    "NEW",
    "PENDING",
    "IN_PROGRESS",
    "COMPLETED",
    "FAILED",
    "CANCELLED",
    name="task_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    task_priority.create(bind, checkfirst=True)
    task_status.create(bind, checkfirst=True)

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", task_priority, nullable=False),
        sa.Column("status", task_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("tasks")

    bind = op.get_bind()
    task_status.drop(bind, checkfirst=True)
    task_priority.drop(bind, checkfirst=True)
