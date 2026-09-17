"""The dashboard shell.

Milestone 1 has no platform data yet, so this returns an *honest* empty state:
streak 0, nothing connected, no Problem of the Day, and a skill snapshot flagged
"insufficient data". No number here is invented. As later milestones add real
sources, this endpoint fills in from the database rather than from placeholders.
"""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.schemas.dashboard import DashboardResponse, PlatformStatus, SkillSnapshot
from app.services import goals_service

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    # Real values from the database. Platforms/skill are still empty (arrive in
    # later milestones); goals and streak are now live from the goal tracker.
    today = date.today()
    todays_goals = goals_service.list_goals(db, user, today)
    summary = goals_service.streak_summary(db, user, today)

    return DashboardResponse(
        streak=summary["streak"],
        platforms={
            "codeforces": PlatformStatus(connected=False, detail="Not connected yet."),
            "leetcode": PlatformStatus(connected=False, detail="Not connected yet."),
        },
        problem_of_the_day={"codeforces": None, "leetcode": None},
        today_goals=todays_goals,
        today_completed=summary["today_completed"],
        skill_snapshot=SkillSnapshot(),
    )
