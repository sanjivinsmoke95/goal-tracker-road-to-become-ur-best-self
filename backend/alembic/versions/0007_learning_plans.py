"""topic_completions + plans (Milestones 8, 10, 11)

Revision ID: 0007_learning
Revises: 0006_mistakes
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_learning"
down_revision = "0006_mistakes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "topic_completions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic_id", sa.String(64), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "topic_id", name="uq_topic_completion"),
    )
    op.create_index("ix_topic_completions_user_id", "topic_completions", ["user_id"])

    op.create_table(
        "uploaded_plans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(255), server_default=""),
        sa.Column("raw_rows", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_uploaded_plans_user_id", "uploaded_plans", ["user_id"])

    op.create_table(
        "learning_plans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), server_default="Learning Plan"),
        sa.Column("goal", sa.String(500), server_default=""),
        sa.Column("duration_days", sa.Integer(), server_default="30"),
        sa.Column("hours_per_day", sa.Integer(), server_default="2"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(16), server_default="generated"),
        sa.Column("status", sa.String(16), server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_learning_plans_user_id", "learning_plans", ["user_id"])

    op.create_table(
        "plan_days",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("plan_id", sa.String(36), sa.ForeignKey("learning_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("tasks", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_plan_days_plan_id", "plan_days", ["plan_id"])


def downgrade() -> None:
    op.drop_table("plan_days")
    op.drop_table("learning_plans")
    op.drop_table("uploaded_plans")
    op.drop_table("topic_completions")
