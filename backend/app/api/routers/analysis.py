"""Submission analysis + recurring mistakes (Milestones 6 & 13)."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import Problem, Submission, User
from app.schemas.analysis import AnalyzeRequest, MistakeSummary, SubmissionDetail
from app.schemas.platform import SubmissionRead
from app.schemas.recommendation import ProblemMini
from app.services import analysis_service

router = APIRouter(tags=["analysis"])


def _owned(db: Session, user: User, sid: str) -> Submission:
    sub = db.get(Submission, sid)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Submission not found.")
    return sub


@router.get("/submissions/{sid}", response_model=SubmissionDetail)
def submission_detail(sid: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    sub = _owned(db, user, sid)
    p = db.get(Problem, sub.problem_id) if sub.problem_id else None
    return {
        "submission": SubmissionRead.model_validate(sub, from_attributes=True),
        "problem": ProblemMini(id=p.id, platform=p.platform, name=p.name, rating=p.rating,
                               difficulty=p.difficulty, tags=p.tags or [], url=p.url) if p else None,
        "analysis": sub.analysis_meta,
    }


@router.post("/submissions/{sid}/analyze")
def analyze(
    sid: str,
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    sub = _owned(db, user, sid)
    if payload.language:
        sub.language = payload.language
    return analysis_service.analyze_submission(db, user, sub, payload.code)


@router.get("/mistakes", response_model=list[MistakeSummary])
def mistakes(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    return analysis_service.recurring_mistakes(db, user)
