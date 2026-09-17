"""Progress over time (Milestone 21) — computed from real stored activity."""

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import Goal, SkillSnapshot, Submission, TopicCompletion, User

router = APIRouter(prefix="/progress", tags=["progress"])

_RANGE_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}


def _d(dt) -> date:
    if isinstance(dt, datetime):
        return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).date()
    return dt


@router.get("")
def progress(
    period: str = Query(default="weekly", alias="range"),  # 'range' shadows the builtin
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    days = _RANGE_DAYS.get(period, 7)
    today = date.today()
    start = today - timedelta(days=days - 1)
    window = [start + timedelta(days=i) for i in range(days)]

    goals = db.execute(select(Goal).where(Goal.user_id == user.id)).scalars()
    goals_by_day: dict[date, int] = defaultdict(int)
    for g in goals:
        if g.status == "completed" and g.date >= start:
            goals_by_day[g.date] += 1

    subs = db.execute(select(Submission).where(Submission.user_id == user.id, Submission.verdict == "OK")).scalars()
    cf_by_day: dict[date, set] = defaultdict(set)
    lc_by_day: dict[date, set] = defaultdict(set)
    tags_practiced: set[str] = set()
    for s in subs:
        d = _d(s.submitted_at)
        if d < start:
            continue
        (cf_by_day if s.platform == "codeforces" else lc_by_day)[d].add(s.problem_id)
        for t in s.problem_tags or []:
            tags_practiced.add(t)

    lessons = db.execute(select(TopicCompletion).where(TopicCompletion.user_id == user.id)).scalars()
    lessons_by_day: dict[date, int] = defaultdict(int)
    lessons_total = 0
    for tc in lessons:
        lessons_total += 1
        d = _d(tc.completed_at)
        if d >= start:
            lessons_by_day[d] += 1

    series = [
        {
            "date": d.isoformat(),
            "goals": goals_by_day.get(d, 0),
            "cf": len(cf_by_day.get(d, set())),
            "lc": len(lc_by_day.get(d, set())),
            "lessons": lessons_by_day.get(d, 0),
        }
        for d in window
    ]

    snaps = list(
        db.execute(
            select(SkillSnapshot).where(SkillSnapshot.user_id == user.id, SkillSnapshot.date >= start)
            .order_by(SkillSnapshot.date)
        ).scalars()
    )
    skill_change = None
    if len(snaps) >= 2 and snaps[0].estimated_rating and snaps[-1].estimated_rating:
        skill_change = snaps[-1].estimated_rating - snaps[0].estimated_rating

    return {
        "range": period,
        "series": series,
        "totals": {
            "goals_completed": sum(s["goals"] for s in series),
            "cf_problems": sum(s["cf"] for s in series),
            "lc_problems": sum(s["lc"] for s in series),
            "lessons_completed": sum(s["lessons"] for s in series),
            "lessons_total": lessons_total,
            "topics_practiced": len(tags_practiced),
        },
        "skill_change": skill_change,
    }
