"""Recurring coding-mistake tracking (Milestones 6 & 13)."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class MistakeOccurrence(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "mistake_occurrences"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    mistake_type: Mapped[str] = mapped_column(String(48), index=True, nullable=False)  # off_by_one, integer_overflow...
    note: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(String(12), default="medium")  # low|medium|high
    platform: Mapped[str] = mapped_column(String(16), default="")
    problem_id: Mapped[str | None] = mapped_column(String(64))
    submission_id: Mapped[str | None] = mapped_column(String(36))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
