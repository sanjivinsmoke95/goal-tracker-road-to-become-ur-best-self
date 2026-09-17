"""Codeforces connect / sync + problem & submission access (Milestone 3)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_cf_adapter, get_current_user
from app.db import get_db
from app.models import CodeforcesProfile, PlatformAccount, Problem, Submission, User
from app.schemas.platform import (
    CodeforcesProfileRead,
    ConnectRequest,
    ProblemRead,
    SubmissionRead,
    SyncResult,
)
from app.services import sync_service
from app.services.adapters.base import PlatformAdapter

platforms = APIRouter(prefix="/platforms/codeforces", tags=["codeforces"])
cf = APIRouter(prefix="/codeforces", tags=["codeforces"])


@platforms.post("/connect", response_model=CodeforcesProfileRead)
def connect(
    payload: ConnectRequest,
    adapter: PlatformAdapter = Depends(get_cf_adapter),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CodeforcesProfile:
    try:
        sync_service.sync_codeforces(db, user, payload.handle.strip(), adapter)
    except Exception as exc:  # adapter/network errors surface as 400
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return db.execute(select(CodeforcesProfile).where(CodeforcesProfile.user_id == user.id)).scalar_one()


@platforms.post("/sync", response_model=SyncResult)
def sync(
    adapter: PlatformAdapter = Depends(get_cf_adapter),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    account = db.execute(
        select(PlatformAccount).where(
            PlatformAccount.user_id == user.id, PlatformAccount.platform == "codeforces"
        )
    ).scalar_one_or_none()
    if not account:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Connect a Codeforces handle first.")
    try:
        return sync_service.sync_codeforces(db, user, account.handle, adapter)
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@cf.get("/profile", response_model=CodeforcesProfileRead | None)
def profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.execute(select(CodeforcesProfile).where(CodeforcesProfile.user_id == user.id)).scalar_one_or_none()


@cf.get("/problems", response_model=list[ProblemRead])
def problems(
    solved: bool | None = Query(default=None),
    min_rating: int | None = Query(default=None),
    max_rating: int | None = Query(default=None),
    tag: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Problem]:
    solved_ids = set(
        db.execute(
            select(Submission.problem_id).where(
                Submission.user_id == user.id, Submission.verdict == "OK"
            )
        ).scalars()
    )
    stmt = select(Problem).where(Problem.platform == "codeforces")
    if min_rating is not None:
        stmt = stmt.where(Problem.rating >= min_rating)
    if max_rating is not None:
        stmt = stmt.where(Problem.rating <= max_rating)
    rows = list(db.execute(stmt.order_by(Problem.rating).limit(2000)).scalars())
    out = []
    for p in rows:
        if solved is True and p.id not in solved_ids:
            continue
        if solved is False and p.id in solved_ids:
            continue
        if tag and tag not in (p.tags or []):
            continue
        out.append(p)
        if len(out) >= limit:
            break
    return out


@cf.get("/submissions", response_model=list[SubmissionRead])
def submissions(
    verdict: str | None = Query(default=None),
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Submission]:
    stmt = select(Submission).where(Submission.user_id == user.id, Submission.platform == "codeforces")
    if verdict:
        stmt = stmt.where(Submission.verdict == verdict)
    return list(db.execute(stmt.order_by(Submission.submitted_at.desc()).limit(limit)).scalars())
