"""Consent-based friendships for profile comparison.

A comparison only happens when BOTH sides agree: one user sends a request, the
other accepts, and the accepting side can still keep their profile un-comparable
via UserPreferences.allow_comparison. No profile data crosses without that.
"""

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin

STATUSES = ("pending", "accepted", "declined")


class Friendship(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "friendships"
    __table_args__ = (UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),)

    requester_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    addressee_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(12), default="pending", nullable=False)
