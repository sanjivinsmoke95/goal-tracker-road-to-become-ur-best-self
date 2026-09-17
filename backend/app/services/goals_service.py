"""Goal CRUD + the deterministic streak calculation.

The streak counts consecutive days, ending today, that have at least one
completed goal — with a one-day grace period so an as-yet-unworked *today* does
not break yesterday's run. It is computed from real completion dates, never
stored, so it can't drift.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Goal, User


def compute_streak(completed_dates: set[date], today: date) -> int:
    """Pure function — unit-tested directly."""
    if not completed_dates:
        return 0
    if today in completed_dates:
        cursor = today
    elif (today - timedelta(days=1)) in completed_dates:
        cursor = today - timedelta(days=1)  # grace: today isn't over yet
    else:
        return 0
    streak = 0
    while cursor in completed_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def list_goals(db: Session, user: User, on_date: date) -> list[Goal]:
    rows = db.execute(
        select(Goal)
        .where(Goal.user_id == user.id, Goal.date == on_date)
        .order_by(Goal.created_at)
    )
    return list(rows.scalars().all())


def get_goal(db: Session, user: User, goal_id: str) -> Goal | None:
    goal = db.get(Goal, goal_id)
    return goal if goal and goal.user_id == user.id else None


def create_goal(db: Session, user: User, data: dict, today: date) -> Goal:
    payload = dict(data)
    payload.setdefault("date", None)
    if payload["date"] is None:
        payload["date"] = today
    goal = Goal(user_id=user.id, **payload)
    db.add(goal)
    db.flush()
    return goal


def update_goal(db: Session, goal: Goal, changes: dict) -> Goal:
    for key, value in changes.items():
        setattr(goal, key, value)
    # Keep completed_at consistent with status.
    if "status" in changes:
        goal.completed_at = datetime.now(timezone.utc) if changes["status"] == "completed" else None
    db.flush()
    return goal


def toggle_complete(db: Session, goal: Goal) -> Goal:
    if goal.status == "completed":
        goal.status = "pending"
        goal.completed_at = None
    else:
        goal.status = "completed"
        goal.completed_at = datetime.now(timezone.utc)
    db.flush()
    return goal


def delete_goal(db: Session, goal: Goal) -> None:
    db.delete(goal)
    db.flush()


def completed_dates(db: Session, user: User) -> set[date]:
    rows = db.execute(
        select(Goal.date).where(Goal.user_id == user.id, Goal.status == "completed").distinct()
    )
    return {d for (d,) in rows.all()}


def streak_summary(db: Session, user: User, today: date):
    todays = list_goals(db, user, today)
    return {
        "streak": compute_streak(completed_dates(db, user), today),
        "today_total": len(todays),
        "today_completed": sum(1 for g in todays if g.status == "completed"),
    }
