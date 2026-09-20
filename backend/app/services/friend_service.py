"""Friendship lifecycle: request → accept/decline, list, remove.

A friendship is one row per ordered pair, but "are they friends?" is symmetric:
an accepted row in either direction connects the two users.
"""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Friendship, User


def find_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email.strip().lower())).scalar_one_or_none()


def _between(db: Session, a: str, b: str) -> Friendship | None:
    return db.execute(
        select(Friendship).where(
            or_(
                (Friendship.requester_id == a) & (Friendship.addressee_id == b),
                (Friendship.requester_id == b) & (Friendship.addressee_id == a),
            )
        )
    ).scalar_one_or_none()


def send_request(db: Session, me: User, target: User) -> Friendship:
    if target.id == me.id:
        raise ValueError("You can't friend yourself.")
    existing = _between(db, me.id, target.id)
    if existing:
        if existing.status == "accepted":
            raise ValueError("You're already friends.")
        if existing.status == "pending":
            # If they already invited me, accept it instead of duplicating.
            if existing.addressee_id == me.id:
                existing.status = "accepted"
                db.flush()
                return existing
            raise ValueError("A request is already pending.")
        # Previously declined → allow a fresh request from me.
        existing.requester_id, existing.addressee_id, existing.status = me.id, target.id, "pending"
        db.flush()
        return existing
    fr = Friendship(requester_id=me.id, addressee_id=target.id, status="pending")
    db.add(fr)
    db.flush()
    return fr


def respond(db: Session, me: User, friendship_id: str, accept: bool) -> Friendship:
    fr = db.get(Friendship, friendship_id)
    if not fr or fr.addressee_id != me.id or fr.status != "pending":
        raise ValueError("No such pending request.")
    fr.status = "accepted" if accept else "declined"
    db.flush()
    return fr


def remove(db: Session, me: User, other_id: str) -> None:
    fr = _between(db, me.id, other_id)
    if fr:
        db.delete(fr)
        db.flush()


def are_friends(db: Session, a: str, b: str) -> bool:
    fr = _between(db, a, b)
    return bool(fr and fr.status == "accepted")


def list_friends(db: Session, me: User) -> list[User]:
    rows = db.execute(
        select(Friendship).where(
            Friendship.status == "accepted",
            or_(Friendship.requester_id == me.id, Friendship.addressee_id == me.id),
        )
    ).scalars()
    ids = [fr.addressee_id if fr.requester_id == me.id else fr.requester_id for fr in rows]
    if not ids:
        return []
    return list(db.execute(select(User).where(User.id.in_(ids))).scalars())


def pending(db: Session, me: User) -> dict:
    incoming = db.execute(
        select(Friendship).where(Friendship.addressee_id == me.id, Friendship.status == "pending")
    ).scalars()
    outgoing = db.execute(
        select(Friendship).where(Friendship.requester_id == me.id, Friendship.status == "pending")
    ).scalars()
    return {"incoming": list(incoming), "outgoing": list(outgoing)}
