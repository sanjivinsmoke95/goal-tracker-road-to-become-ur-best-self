"""Get-or-create per-user preferences."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserPreferences


def get_or_create(db: Session, user: User) -> UserPreferences:
    prefs = db.execute(
        select(UserPreferences).where(UserPreferences.user_id == user.id)
    ).scalar_one_or_none()
    if prefs is None:
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)
        db.flush()
    return prefs


def update(db: Session, user: User, changes: dict) -> UserPreferences:
    prefs = get_or_create(db, user)
    for key, value in changes.items():
        setattr(prefs, key, value)
    db.flush()
    return prefs
