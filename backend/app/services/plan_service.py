"""Parse uploads, generate plans via AI, and adapt them to real progress.

The parse and adaptation logic are pure functions (unit-tested). Adaptation
preserves the plan's deadline: it redistributes unfinished work across the
remaining days rather than extending the plan.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LearningPlan, PlanDay, User
from app.services.ai import get_provider

_CATEGORY_ALIASES = {
    "cf": "cf", "codeforces": "cf", "lc": "lc", "leetcode": "lc",
    "react": "react", "frontend": "react", "backend": "backend", "be": "backend",
    "cs": "cs", "dsa": "cf",
}


def _norm_category(value: str) -> str:
    return _CATEGORY_ALIASES.get((value or "").strip().lower(), "other")


def parse_upload(content: bytes, filename: str) -> list[dict]:
    """Return [{day, tasks:[{category,title,done}]}] from a CSV or JSON upload."""
    name = filename.lower()
    if name.endswith(".json"):
        return _parse_json(content)
    return _parse_csv(content)


def _parse_json(content: bytes) -> list[dict]:
    data = json.loads(content.decode("utf-8"))
    rows = data.get("days") if isinstance(data, dict) else data
    days: dict[int, list[dict]] = {}
    for r in rows or []:
        d = int(r.get("day") or r.get("Day") or 1)
        for t in r.get("tasks", []) if "tasks" in r else [r]:
            title = t.get("task") or t.get("Task") or t.get("title") or t.get("topic") or t.get("Topic") or ""
            cat = _norm_category(t.get("category") or t.get("Category") or "")
            if title:
                days.setdefault(d, []).append({"category": cat, "title": title, "done": False})
    return _as_day_list(days)


def _parse_csv(content: bytes) -> list[dict]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    days: dict[int, list[dict]] = {}
    for row in reader:
        low = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
        try:
            d = int(low.get("day") or 1)
        except ValueError:
            continue
        title = low.get("task") or low.get("topic") or ""
        if low.get("topic") and low.get("task") and low["topic"] != low["task"]:
            title = f"{low['task']} — {low['topic']}"
        cat = _norm_category(low.get("category", ""))
        if title:
            days.setdefault(d, []).append({"category": cat, "title": title, "done": False})
    return _as_day_list(days)


def _as_day_list(days: dict[int, list[dict]]) -> list[dict]:
    return [{"day": d, "tasks": days[d]} for d in sorted(days)]


def create_plan(db: Session, user: User, title: str, goal: str, day_dicts: list[dict], source: str,
                hours_per_day: int = 2, start: date | None = None) -> LearningPlan:
    start = start or date.today()
    plan = LearningPlan(
        user_id=user.id, title=title, goal=goal, duration_days=len(day_dicts) or 1,
        hours_per_day=hours_per_day, start_date=start, source=source,
    )
    db.add(plan)
    db.flush()
    for entry in day_dicts:
        n = int(entry["day"])
        db.add(PlanDay(plan_id=plan.id, day_number=n, date=start + timedelta(days=n - 1), tasks=entry["tasks"]))
    db.flush()
    return plan


def generate_plan(db: Session, user: User, goal: str, duration_days: int, hours_per_day: int,
                  current_level: int | None = None) -> LearningPlan:
    days = get_provider().generate_plan({
        "goal": goal, "duration_days": duration_days, "hours_per_day": hours_per_day, "current_level": current_level,
    })
    # Normalise categories from the provider output.
    for d in days:
        for t in d.get("tasks", []):
            t["category"] = _norm_category(t.get("category", ""))
            t.setdefault("done", False)
    return create_plan(db, user, f"Plan: {goal[:60]}", goal, days, "generated", hours_per_day)


def current_plan(db: Session, user: User) -> LearningPlan | None:
    return db.execute(
        select(LearningPlan).where(LearningPlan.user_id == user.id, LearningPlan.status == "active")
        .order_by(LearningPlan.created_at.desc())
    ).scalars().first()


# ---- Adaptive rebalancing (pure over PlanDay-like dicts) ----

def rebalance(days: list[dict], today: date) -> list[dict]:
    """Move unfinished tasks from past/overdue days onto the remaining days,
    keeping the final day fixed. `days` items: {date, tasks:[{done,...}]}.
    Returns the mutated list (tasks redistributed)."""
    overdue: list[dict] = []
    future_idx: list[int] = []
    for i, d in enumerate(days):
        d_date = d["date"]
        if d_date < today:
            keep = [t for t in d["tasks"] if t.get("done")]
            moved = [t for t in d["tasks"] if not t.get("done")]
            d["tasks"] = keep
            overdue.extend(moved)
        elif d_date >= today:
            future_idx.append(i)
    if not future_idx or not overdue:
        return days
    # Round-robin the overdue tasks across the remaining days.
    for j, task in enumerate(overdue):
        target = days[future_idx[j % len(future_idx)]]
        target["tasks"] = target["tasks"] + [task]
    return days


def adapt_plan(db: Session, user: User, plan: LearningPlan, today: date | None = None) -> dict:
    today = today or date.today()
    day_dicts = [{"_row": pd, "date": pd.date, "tasks": list(pd.tasks or [])} for pd in plan.days]
    moved_before = sum(1 for d in day_dicts if d["date"] < today for t in d["tasks"] if not t.get("done"))
    rebalance(day_dicts, today)
    for d in day_dicts:
        d["_row"].tasks = d["tasks"]
    db.flush()
    return {"redistributed_tasks": moved_before}
