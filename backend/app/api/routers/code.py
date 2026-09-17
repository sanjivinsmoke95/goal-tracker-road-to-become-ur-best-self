"""Isolated code execution (Milestone 9)."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models import User
from app.services.sandbox import SUPPORTED, run_code

router = APIRouter(prefix="/code", tags=["code"])


class RunRequest(BaseModel):
    language: str
    code: str = Field(default="", max_length=100_000)
    stdin: str = Field(default="", max_length=100_000)


@router.get("/languages")
def languages(_: User = Depends(get_current_user)) -> dict:
    return {"supported": SUPPORTED}


@router.post("/run")
def run(payload: RunRequest, _: User = Depends(get_current_user)) -> dict:
    if payload.language.lower() not in SUPPORTED:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Unsupported language. Try: {', '.join(SUPPORTED)}")
    return asdict(run_code(payload.language, payload.code, payload.stdin))
