"""daily_problems (Milestones 5 & 7)

Revision ID: 0005_daily
Revises: 0004_skills
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_daily"
down_revision = "0004_skills"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daily_problems",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(16), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("problem_id", sa.String(64), sa.ForeignKey("problems.id")),
        sa.Column("target_rating", sa.Integer()),
        sa.Column("score", sa.Float(), server_default="0"),
        sa.Column("reason", sa.JSON()),
        sa.Column("explanation", sa.Text(), server_default=""),
        sa.Column("status", sa.String(16), server_default="assigned"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "platform", "date", name="uq_daily_problem"),
    )
    op.create_index("ix_daily_problems_user_id", "daily_problems", ["user_id"])
    op.create_index("ix_daily_problems_date", "daily_problems", ["date"])


def downgrade() -> None:
    op.drop_table("daily_problems")
