"""platforms, problems, submissions (Milestone 3)

Revision ID: 0003_platforms
Revises: 0002_goals
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_platforms"
down_revision = "0002_goals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "platform_accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(16), nullable=False),
        sa.Column("handle", sa.String(120), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "platform", name="uq_platform_account"),
    )
    op.create_index("ix_platform_accounts_user_id", "platform_accounts", ["user_id"])

    op.create_table(
        "codeforces_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("handle", sa.String(120), nullable=False),
        sa.Column("rating", sa.Integer()),
        sa.Column("max_rating", sa.Integer()),
        sa.Column("rank", sa.String(48)),
        sa.Column("max_rank", sa.String(48)),
        sa.Column("avatar", sa.String(255)),
        sa.Column("last_synced_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "problems",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("platform", sa.String(16), nullable=False),
        sa.Column("external_id", sa.String(48), nullable=False),
        sa.Column("contest_id", sa.Integer()),
        sa.Column("index", sa.String(8)),
        sa.Column("name", sa.String(300), server_default=""),
        sa.Column("rating", sa.Integer()),
        sa.Column("difficulty", sa.String(16)),
        sa.Column("tags", sa.JSON()),
        sa.Column("url", sa.String(300), server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_problems_platform", "problems", ["platform"])
    op.create_index("ix_problems_rating", "problems", ["rating"])
    op.create_index("ix_problems_external_id", "problems", ["external_id"])

    op.create_table(
        "submissions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(16), nullable=False),
        sa.Column("external_id", sa.String(48), nullable=False),
        sa.Column("problem_id", sa.String(64), sa.ForeignKey("problems.id")),
        sa.Column("verdict", sa.String(32), server_default=""),
        sa.Column("language", sa.String(48), server_default=""),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("problem_rating", sa.Integer()),
        sa.Column("problem_tags", sa.JSON()),
        sa.Column("source_available", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("source_code", sa.Text()),
        sa.Column("analysis_meta", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_submissions_user_id", "submissions", ["user_id"])
    op.create_index("ix_submissions_submitted_at", "submissions", ["submitted_at"])
    op.create_index("ix_submissions_problem_id", "submissions", ["problem_id"])


def downgrade() -> None:
    op.drop_table("submissions")
    op.drop_table("problems")
    op.drop_table("codeforces_profiles")
    op.drop_table("platform_accounts")
