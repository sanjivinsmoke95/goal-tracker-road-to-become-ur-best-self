"""LeetCode connect / sync / import + problem access (Milestone 12)."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_lc_adapter
from app.db import get_db
from app.models import PlatformAccount, Problem, Submission, User
from app.schemas.platform import ConnectRequest, ProblemRead
from app.services import skill_engine, sync_service
from app.services.adapters.base import PlatformAdapter

platforms = APIRouter(prefix="/platforms/leetcode", tags=["leetcode"])
lc = APIRouter(prefix="/leetcode", tags=["leetcode"])


@platforms.post("/connect")
def connect(
    payload: ConnectRequest,
    adapter: PlatformAdapter = Depends(get_lc_adapter),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        return sync_service.sync_leetcode(db, user, payload.handle.strip(), adapter)
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@platforms.post("/sync")
def sync(
    adapter: PlatformAdapter = Depends(get_lc_adapter),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    acc = db.execute(
        select(PlatformAccount).where(PlatformAccount.user_id == user.id, PlatformAccount.platform == "leetcode")
    ).scalar_one_or_none()
    if not acc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Connect a LeetCode username first.")
    try:
        return sync_service.sync_leetcode(db, user, acc.handle, adapter)
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@platforms.post("/import")
def import_solved(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Manual import fallback: {items: [{slug, title, difficulty, tags}]}."""
    items = payload.get("items") or []
    if not isinstance(items, list) or not items:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Provide a non-empty 'items' list.")
    return sync_service.import_leetcode_solved(db, user, items)


@lc.get("/profile")
def profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    acc = db.execute(
        select(PlatformAccount).where(PlatformAccount.user_id == user.id, PlatformAccount.platform == "leetcode")
    ).scalar_one_or_none()
    solved = db.execute(
        select(func.count()).select_from(Submission).where(
            Submission.user_id == user.id, Submission.platform == "leetcode", Submission.verdict == "OK"
        )
    ).scalar_one()
    est = skill_engine.compute_for_user(db, user, platform="leetcode").estimated_rating
    level = None
    if est is not None:
        level = "Easy" if est < 1150 else "Medium" if est < 1700 else "Hard"
    return {"connected": acc is not None, "handle": acc.handle if acc else None, "solved": solved, "estimated_level": level}


@lc.get("/problems", response_model=list[ProblemRead])
def problems(
    solved: bool | None = Query(default=None),
    difficulty: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Problem]:
    solved_ids = set(
        db.execute(
            select(Submission.problem_id).where(Submission.user_id == user.id, Submission.verdict == "OK")
        ).scalars()
    )
    rows = list(db.execute(select(Problem).where(Problem.platform == "leetcode")).scalars())
    out = []
    for p in rows:
        if solved is True and p.id not in solved_ids:
            continue
        if solved is False and p.id in solved_ids:
            continue
        if difficulty and (p.difficulty or "").lower() != difficulty.lower():
            continue
        out.append(p)
        if len(out) >= limit:
            break
    return out
