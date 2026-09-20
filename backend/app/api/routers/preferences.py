"""User preferences: personalization inputs + comparison-consent flag."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.schemas.social import PreferencesRead, PreferencesUpdate
from app.services import preferences_service

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=PreferencesRead)
def get_preferences(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return preferences_service.get_or_create(db, user)


@router.put("", response_model=PreferencesRead)
def update_preferences(
    payload: PreferencesUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return preferences_service.update(db, user, payload.model_dump(exclude_unset=True))
