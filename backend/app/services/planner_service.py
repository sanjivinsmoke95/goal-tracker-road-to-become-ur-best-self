"""The daily planner: routines that fill each day, bulk task entry, and the
missed-task carry-over.

Design notes
------------
* Tasks are ordinary ``Goal`` rows — the planner adds *provenance* (source,
  routine_id, carried_from), not a parallel task system, so streaks and the
  dashboard keep working unchanged.
* Routine materialisation is idempotent: a routine produces at most one task per
  day (deduped on routine_id + date), and only for today or the future — we
  never fabricate history.
* "Missed" is derived, not stored: any task still open (pending/in_progress) on a
  day before today is missed. You then move it to today or dismiss it; nothing
  moves on its own.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Goal, Routine, User
from app.services import goals_service

_ALIASES = {
    "cf": "cf", "codeforces": "cf", "dsa": "cf", "cp": "cf",
    "lc": "lc", "leetcode": "lc",
    "react": "react", "frontend": "react", "fe": "react",
    "backend": "backend", "be": "backend", "api": "backend",
    "cs": "cs", "theory": "cs",
}
_PRIORITIES = {"low", "medium", "high"}


def _norm_category(value: str) -> str:
    return _ALIASES.get((value or "").strip().lower(), "other")


# ---------------------------------------------------------------------------
# Paste / bulk parsing
# ---------------------------------------------------------------------------
def parse_paste(text: str) -> list[dict]:
    """One task per line. Optional 'category: title' or '[high] title' prefixes.

    Examples that all work::

        Solve 2 LeetCode mediums
        lc: Two Sum follow-up
        [high] Revise segment trees
        cf | Div 2 virtual contest
    """
    out: list[dict] = []
    for raw in (text or "").splitlines():
        line = raw.strip().lstrip("-*•").strip()
        if not line:
            continue
        priority = "medium"
        # [high] / [low] priority marker anywhere at the start
        if line.startswith("[") and "]" in line:
            tag = line[1 : line.index("]")].strip().lower()
            if tag in _PRIORITIES:
                priority = tag
                line = line[line.index("]") + 1 :].strip()
        category = "other"
        for sep in (":", "|", "—", "-"):
            if sep in line:
                head, rest = line.split(sep, 1)
                cand = head.strip().lower()
                if cand in _ALIASES and rest.strip():
                    category = _ALIASES[cand]
                    line = rest.strip()
                break
        if line:
            out.append(
                {"title": line[:200], "category": category, "priority": priority, "estimated_minutes": 0}
            )
    return out


# ---------------------------------------------------------------------------
# Routines
# ---------------------------------------------------------------------------
def effective_days(routine: Routine) -> set[int]:
    if routine.frequency == "daily":
        return set(range(7))
    if routine.frequency == "weekdays":
        return {0, 1, 2, 3, 4}
    return {int(d) for d in (routine.days_of_week or [])}


def applies_on(routine: Routine, on_date: date) -> bool:
    return bool(routine.active) and on_date.weekday() in effective_days(routine)


def list_routines(db: Session, user: User) -> list[Routine]:
    return list(
        db.execute(
            select(Routine).where(Routine.user_id == user.id).order_by(Routine.created_at)
        ).scalars()
    )


def get_routine(db: Session, user: User, routine_id: str) -> Routine | None:
    r = db.get(Routine, routine_id)
    return r if r and r.user_id == user.id else None


def create_routine(db: Session, user: User, data: dict) -> Routine:
    routine = Routine(user_id=user.id, **data)
    db.add(routine)
    db.flush()
    return routine


def update_routine(db: Session, routine: Routine, changes: dict) -> Routine:
    for key, value in changes.items():
        setattr(routine, key, value)
    db.flush()
    return routine


def delete_routine(db: Session, routine: Routine) -> None:
    # The tasks it already spawned are real tasks; leave them, just cut the link
    # so a deleted routine can't be blamed for them.
    for g in db.execute(
        select(Goal).where(Goal.routine_id == routine.id)
    ).scalars():
        g.routine_id = None
    db.delete(routine)
    db.flush()


def materialize_routines(db: Session, user: User, on_date: date, today: date) -> int:
    """Create today's (or a future day's) routine tasks that don't exist yet.

    Idempotent and past-safe: nothing is created for days before today.
    Returns the number of tasks created.
    """
    if on_date < today:
        return 0
    existing = set(
        db.execute(
            select(Goal.routine_id).where(
                Goal.user_id == user.id, Goal.date == on_date, Goal.routine_id.is_not(None)
            )
        ).scalars()
    )
    created = 0
    for routine in list_routines(db, user):
        if not applies_on(routine, on_date) or routine.id in existing:
            continue
        db.add(
            Goal(
                user_id=user.id,
                title=routine.title,
                description=routine.description,
                category=routine.category,
                priority=routine.priority,
                estimated_minutes=routine.estimated_minutes,
                date=on_date,
                status="pending",
                source="routine",
                routine_id=routine.id,
            )
        )
        created += 1
    if created:
        db.flush()
    return created


# ---------------------------------------------------------------------------
# Day view + bulk add + missed carry-over
# ---------------------------------------------------------------------------
def day_plan(db: Session, user: User, on_date: date, today: date) -> dict:
    materialize_routines(db, user, on_date, today)
    tasks = goals_service.list_goals(db, user, on_date)
    completed = sum(1 for t in tasks if t.status == "completed")
    return {
        "date": on_date,
        "tasks": tasks,
        "total": len(tasks),
        "completed": completed,
        "streak": goals_service.compute_streak(goals_service.completed_dates(db, user), today),
    }


def bulk_create(db: Session, user: User, items: list[dict], on_date: date, source: str) -> list[Goal]:
    made: list[Goal] = []
    for item in items:
        goal = Goal(
            user_id=user.id,
            title=item["title"],
            category=item.get("category", "other"),
            priority=item.get("priority", "medium"),
            estimated_minutes=item.get("estimated_minutes", 0),
            date=on_date,
            status="pending",
            source=source,
        )
        db.add(goal)
        made.append(goal)
    if made:
        db.flush()
    return made


def missed_tasks(db: Session, user: User, today: date) -> list[Goal]:
    """Open tasks from any day before today — the carry-over candidates."""
    return list(
        db.execute(
            select(Goal)
            .where(
                Goal.user_id == user.id,
                Goal.date < today,
                Goal.status.in_(("pending", "in_progress")),
            )
            .order_by(Goal.date, Goal.created_at)
        ).scalars()
    )


def move_to_today(db: Session, goal: Goal, today: date) -> Goal:
    """Carry a missed task into today, remembering where it came from."""
    if goal.carried_from is None:
        goal.carried_from = goal.date
    goal.date = today
    goal.status = "pending"
    goal.completed_at = None
    if goal.source != "routine":
        goal.source = "carried"
    db.flush()
    return goal


def dismiss(db: Session, goal: Goal) -> Goal:
    """Give up on a missed task — it leaves the missed list without moving."""
    goal.status = "skipped"
    goal.completed_at = None
    db.flush()
    return goal
