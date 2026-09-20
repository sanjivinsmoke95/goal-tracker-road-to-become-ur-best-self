"""rag corpus: documents + fitted-index meta

Revision ID: 0010_rag
Revises: 0009_planner
Create Date: 2026-09-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_rag"
down_revision = "0009_planner"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rag_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("topic", sa.String(length=48), nullable=False, server_default="general"),
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rag_documents_topic", "rag_documents", ["topic"])

    op.create_table(
        "rag_meta",
        sa.Column("id", sa.String(length=24), nullable=False),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("rag_meta")
    op.drop_index("ix_rag_documents_topic", table_name="rag_documents")
    op.drop_table("rag_documents")
