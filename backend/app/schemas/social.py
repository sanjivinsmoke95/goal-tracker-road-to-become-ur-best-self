from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Friends --------------------------------------------------------------
class FriendRequestCreate(BaseModel):
    email: EmailStr


class UserMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: str


class FriendRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    requester_id: str
    addressee_id: str
    status: str


class PendingRequests(BaseModel):
    incoming: list[FriendRequestRead]
    outgoing: list[FriendRequestRead]


# --- Preferences ----------------------------------------------------------
Difficulty = Literal["weakness", "current", "challenge", "balanced"]


class PreferencesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    display_name: str
    daily_hours: float
    daily_problems: int
    target_cf_rating: int | None
    target_lc_solved: int | None
    desired_difficulty: str
    technologies: list[str]
    goals: str
    allow_comparison: bool


class PreferencesUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=80)
    daily_hours: float | None = Field(default=None, ge=0, le=24)
    daily_problems: int | None = Field(default=None, ge=0, le=50)
    target_cf_rating: int | None = Field(default=None, ge=0, le=4000)
    target_lc_solved: int | None = Field(default=None, ge=0, le=10000)
    desired_difficulty: Difficulty | None = None
    technologies: list[str] | None = None
    goals: str | None = Field(default=None, max_length=4000)
    allow_comparison: bool | None = None
