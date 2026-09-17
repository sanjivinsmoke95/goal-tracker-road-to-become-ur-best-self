"""Problem of the Day (Milestones 5 & 7)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import DailyProblem, Problem, User
from app.schemas.recommendation import DailyProblemRead, ProblemMini, ProblemOfTheDay
from app.services import recommendations_service

router = APIRouter(tags=["recommendations"])


def _serialize(db: Session, dp: DailyProblem | None) -> DailyProblemRead | None:
    if dp is None:
        return None
    p: Problem | None = db.get(Problem, dp.problem_id) if dp.problem_id else None
    return DailyProblemRead(
        platform=dp.platform,
        date=dp.date,
        problem=ProblemMini(
            id=p.id, platform=p.platform, name=p.name, rating=p.rating,
            difficulty=p.difficulty, tags=p.tags or [], url=p.url,
        ) if p else None,
        target_rating=dp.target_rating,
        score=dp.score,
        reason=dp.reason or {},
        explanation=dp.explanation,
        status=dp.status,
    )


@router.get("/problems/today", response_model=ProblemOfTheDay)
@router.get("/recommendations/today", response_model=ProblemOfTheDay)
def problems_today(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ProblemOfTheDay:
    cf = recommendations_service.pick_daily(db, user, "codeforces")
    lc = recommendations_service.pick_daily(db, user, "leetcode")
    return ProblemOfTheDay(codeforces=_serialize(db, cf), leetcode=_serialize(db, lc))
