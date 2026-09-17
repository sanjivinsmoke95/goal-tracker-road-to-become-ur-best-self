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
from app.models import CodeforcesProfile
from app.schemas.dashboard import DashboardResponse, PlatformStatus, SkillSnapshot
from app.services import goals_service, skill_engine

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    # Real values from the database. Platforms/skill are still empty (arrive in
    # later milestones); goals and streak are now live from the goal tracker.
    from sqlalchemy import select

    today = date.today()
    todays_goals = goals_service.list_goals(db, user, today)
    summary = goals_service.streak_summary(db, user, today)

    from app.models import PlatformAccount

    cf = db.execute(select(CodeforcesProfile).where(CodeforcesProfile.user_id == user.id)).scalar_one_or_none()
    cf_status = (
        PlatformStatus(connected=True, handle=cf.handle, detail=f"Synced · rating {cf.rating or '—'}")
        if cf
        else PlatformStatus(connected=False, detail="Not connected yet.")
    )
    lc_acc = db.execute(
        select(PlatformAccount).where(PlatformAccount.user_id == user.id, PlatformAccount.platform == "leetcode")
    ).scalar_one_or_none()
    lc_status = (
        PlatformStatus(connected=True, handle=lc_acc.handle, detail="Synced")
        if lc_acc
        else PlatformStatus(connected=False, detail="Not connected yet.")
    )

    from app.services.adapters.leetcode import blended_rating, level_from_rating

    lc_est = (blended_rating(lc_acc.meta) if lc_acc else None) or skill_engine.compute_for_user(
        db, user, platform="leetcode"
    ).estimated_rating
    lc_level = level_from_rating(lc_est)

    profile = skill_engine.compute_for_user(db, user, platform="codeforces")
    if profile.estimated_rating is not None or profile.topics:
        skill = SkillSnapshot(
            available=True,
            estimated_cf_rating=profile.estimated_rating,
            estimated_lc_level=lc_level,
            strong_topics=profile.strengths[:4],
            reinforce_topics=profile.reinforce[:4],
            note="Estimated from your recent solved-problem ratings and topic success rates.",
        )
    elif lc_level is not None:
        skill = SkillSnapshot(available=True, estimated_lc_level=lc_level,
                              note="Estimated from your LeetCode solving history.")
    else:
        skill = SkillSnapshot()

    return DashboardResponse(
        streak=summary["streak"],
        platforms={
            "codeforces": cf_status,
            "leetcode": lc_status,
        },
        problem_of_the_day={"codeforces": None, "leetcode": None},
        today_goals=todays_goals,
        today_completed=summary["today_completed"],
        skill_snapshot=skill,
    )
