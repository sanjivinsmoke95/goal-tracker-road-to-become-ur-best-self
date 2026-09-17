"""skill_snapshots (Milestone 4)

Revision ID: 0004_skills
Revises: 0003_platforms
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_skills"
down_revision = "0003_platforms"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "skill_snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("estimated_rating", sa.Integer()),
        sa.Column("confidence", sa.Float(), server_default="0"),
        sa.Column("recent_success_rate", sa.Float()),
        sa.Column("total_solved", sa.Integer(), server_default="0"),
        sa.Column("total_attempts", sa.Integer(), server_default="0"),
        sa.Column("topics", sa.JSON()),
        sa.Column("platform", sa.String(16), server_default="codeforces"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "date", name="uq_skill_snapshot_day"),
    )
    op.create_index("ix_skill_snapshots_user_id", "skill_snapshots", ["user_id"])
    op.create_index("ix_skill_snapshots_date", "skill_snapshots", ["date"])


def downgrade() -> None:
    op.drop_table("skill_snapshots")
