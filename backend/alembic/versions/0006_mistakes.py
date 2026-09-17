"""mistake_occurrences (Milestone 6)

Revision ID: 0006_mistakes
Revises: 0005_daily
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_mistakes"
down_revision = "0005_daily"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mistake_occurrences",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mistake_type", sa.String(48), nullable=False),
        sa.Column("note", sa.Text(), server_default=""),
        sa.Column("severity", sa.String(12), server_default="medium"),
        sa.Column("platform", sa.String(16), server_default=""),
        sa.Column("problem_id", sa.String(64)),
        sa.Column("submission_id", sa.String(36)),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_mistake_occurrences_user_id", "mistake_occurrences", ["user_id"])
    op.create_index("ix_mistake_occurrences_mistake_type", "mistake_occurrences", ["mistake_type"])


def downgrade() -> None:
    op.drop_table("mistake_occurrences")
