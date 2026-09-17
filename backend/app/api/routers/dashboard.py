"""The dashboard shell.

Milestone 1 has no platform data yet, so this returns an *honest* empty state:
streak 0, nothing connected, no Problem of the Day, and a skill snapshot flagged
"insufficient data". No number here is invented. As later milestones add real
sources, this endpoint fills in from the database rather than from placeholders.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.schemas.dashboard import DashboardResponse, PlatformStatus, SkillSnapshot

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    # Everything below reflects real state. There are no platform accounts,
    # submissions, goals, or skill history yet, so we report exactly that.
    return DashboardResponse(
        streak=0,
        platforms={
            "codeforces": PlatformStatus(connected=False, detail="Not connected yet."),
            "leetcode": PlatformStatus(connected=False, detail="Not connected yet."),
        },
        problem_of_the_day={"codeforces": None, "leetcode": None},
        today_goals=[],
        skill_snapshot=SkillSnapshot(),
    )
