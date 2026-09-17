"""Dashboard response shapes.

The types deliberately model *absence* of data ("insufficient_data") as a
first-class state. In Milestone 1 nothing is connected yet, so the dashboard
returns an honest empty shell — never invented numbers. Real values arrive as
later milestones (goals, Codeforces sync, skill engine) land.
"""

from pydantic import BaseModel


class PlatformStatus(BaseModel):
    connected: bool
    handle: str | None = None
    detail: str  # human-readable state, e.g. "Not connected yet."


class SkillSnapshot(BaseModel):
    # None until the skill engine (Milestone 4) has enough real submissions.
    available: bool = False
    estimated_cf_rating: int | None = None
    estimated_lc_level: str | None = None
    strong_topics: list[str] = []
    reinforce_topics: list[str] = []
    note: str = "Insufficient data. Connect Codeforces to begin building your skill profile."


class DashboardResponse(BaseModel):
    streak: int
    platforms: dict[str, PlatformStatus]
    problem_of_the_day: dict[str, None]  # {"codeforces": None, "leetcode": None} until M5
    today_goals: list[dict]  # empty until the goal tracker (M2)
    skill_snapshot: SkillSnapshot
    # Small provenance note the UI shows so estimates are never mistaken for facts.
    provenance: dict[str, str] = {
        "data": "What the system knows from your real history.",
        "inference": "What the system estimates from that data.",
        "recommendation": "What the system suggests you do.",
    }
