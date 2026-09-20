"""Isolated code execution (Milestone 9) + static code analysis (DevTrack AI)."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.services import code_analysis
from app.services.sandbox import SUPPORTED, run_code

router = APIRouter(prefix="/code", tags=["code"])


class RunRequest(BaseModel):
    language: str
    code: str = Field(default="", max_length=100_000)
    stdin: str = Field(default="", max_length=100_000)


class AnalyzeRequest(BaseModel):
    language: str = "python"
    code: str = Field(min_length=1, max_length=100_000)
    problem_statement: str = Field(default="", max_length=8000)
    constraints: str = Field(default="", max_length=2000)
    verdict: str = Field(default="", max_length=40)
    question: str = Field(default="", max_length=1000)


@router.get("/languages")
def languages(_: User = Depends(get_current_user)) -> dict:
    return {"supported": SUPPORTED}


@router.post("/run")
def run(payload: RunRequest, _: User = Depends(get_current_user)) -> dict:
    if payload.language.lower() not in SUPPORTED:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Unsupported language. Try: {', '.join(SUPPORTED)}")
    return asdict(run_code(payload.language, payload.code, payload.stdin))


@router.post("/analyze")
def analyze(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    return code_analysis.analyze(db, payload.model_dump())
