"""Learning plan upload / generation / adaptation (Milestones 10 & 11)."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import LearningPlan, PlanDay, UploadedPlan, User
from app.schemas.plan import DayUpdate, GenerateRequest, LearningPlanRead
from app.services import plan_service, skill_engine

router = APIRouter(prefix="/plans", tags=["plans"])

_MAX_UPLOAD = 1_000_000  # 1 MB


def _owned(db: Session, user: User, plan_id: str) -> LearningPlan:
    plan = db.get(LearningPlan, plan_id)
    if not plan or plan.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plan not found.")
    return plan


@router.post("/upload", response_model=LearningPlanRead)
async def upload_plan(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LearningPlan:
    content = await file.read()
    if len(content) > _MAX_UPLOAD:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File too large (max 1 MB).")
    try:
        day_dicts = plan_service.parse_upload(content, file.filename or "plan.csv")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Could not parse the file: {exc}") from exc
    if not day_dicts:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "No plan rows found in the file.")
    db.add(UploadedPlan(user_id=user.id, filename=file.filename or "", raw_rows=day_dicts))
    return plan_service.create_plan(db, user, f"Uploaded: {file.filename}", "", day_dicts, "upload")


@router.post("/generate", response_model=LearningPlanRead)
def generate_plan(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LearningPlan:
    level = skill_engine.compute_for_user(db, user).estimated_rating
    return plan_service.generate_plan(db, user, payload.goal, payload.duration_days, payload.hours_per_day, level)


@router.get("/current", response_model=LearningPlanRead | None)
def get_current(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return plan_service.current_plan(db, user)


@router.post("/{plan_id}/adapt")
def adapt(plan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    plan = _owned(db, user, plan_id)
    return plan_service.adapt_plan(db, user, plan)


@router.patch("/{plan_id}/days/{day_number}", response_model=LearningPlanRead)
def update_day(
    plan_id: str,
    day_number: int,
    payload: DayUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LearningPlan:
    plan = _owned(db, user, plan_id)
    day = next((d for d in plan.days if d.day_number == day_number), None)
    if not day:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Day not found.")
    day.tasks = payload.tasks
    db.flush()
    db.refresh(plan)
    return plan
