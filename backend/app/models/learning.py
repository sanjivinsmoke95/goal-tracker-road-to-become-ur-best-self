"""Per-user learning progress (the catalogue itself lives in curriculum.py)."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class TopicCompletion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "topic_completions"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_topic_completion"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    topic_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
