"""Connected competitive-programming accounts + the Codeforces profile mirror."""

from datetime import datetime

from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class PlatformAccount(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "platform_accounts"
    __table_args__ = (UniqueConstraint("user_id", "platform", name="uq_platform_account"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(16), nullable=False)  # codeforces | leetcode
    handle: Mapped[str] = mapped_column(String(120), nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Platform-specific extras, e.g. LeetCode solved counts by difficulty.
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class CodeforcesProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "codeforces_profiles"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    handle: Mapped[str] = mapped_column(String(120), nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer)
    max_rating: Mapped[int | None] = mapped_column(Integer)
    rank: Mapped[str | None] = mapped_column(String(48))
    max_rank: Mapped[str | None] = mapped_column(String(48))
    avatar: Mapped[str | None] = mapped_column(String(255))
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
