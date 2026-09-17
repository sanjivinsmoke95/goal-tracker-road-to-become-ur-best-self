"""LeetCode adapter (Milestone 12).

LeetCode has no official public API, so this uses the community GraphQL endpoint
for public profile stats + recent accepted problems, and degrades gracefully.
It is deliberately behind the adapter with a manual-import fallback, so the app
never hard-depends on a fragile endpoint.

Difficulty is mapped to a pseudo-rating (Easy 900 / Medium 1400 / Hard 1900) so
the same rating-based skill and recommendation engines work unchanged for LC.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.services.adapters.base import (
    NormalizedProblem,
    NormalizedProfile,
    NormalizedSubmission,
    PlatformAdapter,
)

_GRAPHQL = "https://leetcode.com/graphql"
DIFFICULTY_RATING = {"Easy": 900, "Medium": 1400, "Hard": 1900}


def difficulty_to_rating(difficulty: str | None) -> int | None:
    return DIFFICULTY_RATING.get((difficulty or "").title())


def lc_problem(slug: str, title: str, difficulty: str, tags: list[str]) -> NormalizedProblem:
    return NormalizedProblem(
        platform="leetcode",
        external_id=slug,
        name=title,
        difficulty=difficulty,
        rating=difficulty_to_rating(difficulty),
        tags=tags,
        url=f"https://leetcode.com/problems/{slug}/",
    )


class LeetCodeError(Exception):
    pass


class LeetCodeAdapter(PlatformAdapter):
    platform = "leetcode"

    def __init__(self, client: httpx.Client | None = None):
        self._client = client or httpx.Client(timeout=15, headers={"Referer": "https://leetcode.com"})

    def _query(self, query: str, variables: dict) -> dict:
        try:
            r = self._client.post(_GRAPHQL, json={"query": query, "variables": variables})
            r.raise_for_status()
            return r.json().get("data", {})
        except httpx.HTTPError as exc:
            raise LeetCodeError(f"LeetCode is unreachable: {exc}") from exc

    def fetch_profile(self, handle: str) -> NormalizedProfile:
        q = """query($u:String!){ matchedUser(username:$u){ username
          submitStatsGlobal{ acSubmissionNum{ difficulty count } } } }"""
        data = self._query(q, {"u": handle})
        user = data.get("matchedUser")
        if not user:
            raise LeetCodeError(f"No such LeetCode user: {handle}")
        return NormalizedProfile(handle=user["username"])

    def fetch_submissions(self, handle: str) -> list[NormalizedSubmission]:
        q = """query($u:String!,$n:Int!){ recentAcSubmissionList(username:$u,limit:$n){
          id title titleSlug timestamp } }"""
        data = self._query(q, {"u": handle, "n": 50})
        out: list[NormalizedSubmission] = []
        for s in data.get("recentAcSubmissionList") or []:
            out.append(
                NormalizedSubmission(
                    external_id=str(s["id"]),
                    verdict="OK",
                    language="",
                    submitted_at=datetime.fromtimestamp(int(s["timestamp"]), tz=timezone.utc),
                    problem=NormalizedProblem(
                        platform="leetcode", external_id=s["titleSlug"], name=s["title"],
                        difficulty=None, url=f"https://leetcode.com/problems/{s['titleSlug']}/",
                    ),
                )
            )
        return out
