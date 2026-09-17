"""Daily goals — the habit layer of the OS.

A goal belongs to one day. Statuses move pending → in_progress → completed (or
skipped). Streaks are derived from the days that have at least one completed
goal, so the streak is real activity, never a stored counter that can drift.
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin

# Kept as plain strings (validated in the Pydantic layer) so the schema stays
# portable across Postgres and the SQLite test database.
CATEGORIES = ("cf", "lc", "react", "backend", "cs", "other")
PRIORITIES = ("low", "medium", "high")
STATUSES = ("pending", "in_progress", "completed", "skipped")


class Goal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "goals"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(24), default="other", nullable=False)
    priority: Mapped[str] = mapped_column(String(12), default="medium", nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # The day this goal is scheduled for.
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    notes: Mapped[str] = mapped_column(Text, default="")

    # Optional link to a problem or learning topic (populated in later milestones).
    linked_type: Mapped[str | None] = mapped_column(String(16))  # "problem" | "topic"
    linked_ref: Mapped[str | None] = mapped_column(String(200))
