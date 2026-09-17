"""Build candidates from the DB, pick the daily problem, persist it once/day."""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DailyProblem, Goal, Problem, Submission, User
from app.services import recommendation_engine as reco
from app.services import skill_engine
from app.services.ai import get_provider
from app.services.recommendation_engine import Candidate, RecoContext

_WINDOW = 350  # only score problems within this rating window of the target


def _solved_ids(db: Session, user: User, platform: str) -> set[str]:
    return set(
        db.execute(
            select(Submission.problem_id).where(
                Submission.user_id == user.id, Submission.platform == platform, Submission.verdict == "OK"
            )
        ).scalars()
    )


def _context(db: Session, user: User, platform: str, on_date: date) -> RecoContext:
    now = datetime.now(timezone.utc)
    recent_cut = now - timedelta(days=7)
    subs = list(
        db.execute(
            select(Submission).where(Submission.user_id == user.id, Submission.platform == platform)
        ).scalars()
    )
    recent_ids = {s.problem_id for s in subs if s.problem_id and _aware(s.submitted_at) >= recent_cut}
    last_seen: dict[str, int] = {}
    for s in subs:
        for tag in s.problem_tags or []:
            days = (now - _aware(s.submitted_at)).days
            last_seen[tag] = min(last_seen.get(tag, 10**9), days)
    goal_tags = {
        g.category for g in db.execute(select(Goal).where(Goal.user_id == user.id, Goal.date == on_date)).scalars()
    }
    return RecoContext(recent_problem_ids=recent_ids, tag_last_seen_days=last_seen, goal_tags=goal_tags)


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def pick_daily(db: Session, user: User, platform: str, on_date: date | None = None) -> DailyProblem | None:
    on_date = on_date or date.today()
    existing = db.execute(
        select(DailyProblem).where(
            DailyProblem.user_id == user.id, DailyProblem.platform == platform, DailyProblem.date == on_date
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    profile = skill_engine.compute_for_user(db, user, platform=platform)
    target = reco.adapted_target(profile)
    solved = _solved_ids(db, user, platform)

    rows = list(
        db.execute(
            select(Problem).where(
                Problem.platform == platform,
                Problem.rating.is_not(None),
                Problem.rating >= target - _WINDOW,
                Problem.rating <= target + _WINDOW,
            )
        ).scalars()
    )
    candidates = [Candidate(id=p.id, rating=p.rating, tags=p.tags or []) for p in rows if p.id not in solved]
    if not candidates:
        return None

    ctx = _context(db, user, platform, on_date)
    ranked = reco.rank(candidates, profile, ctx)
    best = ranked[0]
    problem = db.get(Problem, best["id"])

    explanation = get_provider().explain_recommendation(
        {
            "problem_rating": problem.rating,
            "target_rating": target,
            "tags": problem.tags or [],
            "top_reason": best["top_reason"],
        }
    )

    dp = DailyProblem(
        user_id=user.id,
        platform=platform,
        date=on_date,
        problem_id=problem.id,
        target_rating=target,
        score=best["score"],
        reason=best,
        explanation=explanation,
    )
    db.add(dp)
    db.flush()
    return dp
