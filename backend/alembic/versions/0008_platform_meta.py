"""platform_accounts.meta (LeetCode solved counts)

Revision ID: 0008_meta
Revises: 0007_learning
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_meta"
down_revision = "0007_learning"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("platform_accounts", sa.Column("meta", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("platform_accounts", "meta")
