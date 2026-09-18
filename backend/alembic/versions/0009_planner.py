"""planner: routines table + goal provenance columns

Revision ID: 0009_planner
Revises: 0008_meta
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_planner"
down_revision = "0008_meta"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "routines",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("category", sa.String(length=24), nullable=False, server_default="other"),
        sa.Column("priority", sa.String(length=12), nullable=False, server_default="medium"),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("frequency", sa.String(length=12), nullable=False, server_default="daily"),
        sa.Column("days_of_week", sa.JSON(), nullable=True),
        sa.Column("at_time", sa.Time(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_routines_user_id", "routines", ["user_id"])

    op.add_column("goals", sa.Column("source", sa.String(length=16), nullable=False, server_default="manual"))
    op.add_column("goals", sa.Column("routine_id", sa.String(length=36), nullable=True))
    op.add_column("goals", sa.Column("carried_from", sa.Date(), nullable=True))
    op.create_index("ix_goals_routine_id", "goals", ["routine_id"])


def downgrade() -> None:
    op.drop_index("ix_goals_routine_id", table_name="goals")
    op.drop_column("goals", "carried_from")
    op.drop_column("goals", "routine_id")
    op.drop_column("goals", "source")
    op.drop_index("ix_routines_user_id", table_name="routines")
    op.drop_table("routines")
