"""Codeforces adapter — the official public API (no key required).

Honest note: `user.status` returns rich submission *metadata* (verdict, tags,
rating, language, time) but NOT the source code. So `source_code` is always
None here; source is optional and can be supplied manually later.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.services.adapters.base import (
    NormalizedProblem,
    NormalizedProfile,
    NormalizedSubmission,
    PlatformAdapter,
)


class CodeforcesError(Exception):
    pass


class CodeforcesAdapter(PlatformAdapter):
    platform = "codeforces"

    def __init__(self, base_url: str | None = None, client: httpx.Client | None = None):
        self._base = (base_url or settings.codeforces_api_base).rstrip("/")
        self._client = client or httpx.Client(timeout=15)

    def _get(self, method: str, **params) -> list | dict:
        try:
            r = self._client.get(f"{self._base}/{method}", params=params)
            r.raise_for_status()
            data = r.json()
        except httpx.HTTPError as exc:
            raise CodeforcesError(f"Codeforces API unreachable: {exc}") from exc
        if data.get("status") != "OK":
            raise CodeforcesError(data.get("comment", "Codeforces API error"))
        return data["result"]

    def fetch_profile(self, handle: str) -> NormalizedProfile:
        result = self._get("user.info", handles=handle)
        if not result:
            raise CodeforcesError(f"No such handle: {handle}")
        u = result[0]
        return NormalizedProfile(
            handle=u.get("handle", handle),
            rating=u.get("rating"),
            max_rating=u.get("maxRating"),
            rank=u.get("rank"),
            max_rank=u.get("maxRank"),
            avatar=u.get("titlePhoto") or u.get("avatar"),
        )

    def fetch_problemset(self) -> list[NormalizedProblem]:
        """The whole public problem set — the candidate pool for recommendations."""
        result = self._get("problemset.problems")
        out: list[NormalizedProblem] = []
        for p in result.get("problems", []):
            cid, idx = p.get("contestId"), p.get("index")
            if cid is None or idx is None:
                continue
            out.append(
                NormalizedProblem(
                    platform="codeforces",
                    external_id=f"{cid}{idx}",
                    name=p.get("name", ""),
                    contest_id=cid,
                    index=idx,
                    rating=p.get("rating"),
                    tags=p.get("tags", []),
                    url=f"https://codeforces.com/problemset/problem/{cid}/{idx}",
                )
            )
        return out

    def fetch_submissions(self, handle: str) -> list[NormalizedSubmission]:
        rows = self._get("user.status", handle=handle)
        out: list[NormalizedSubmission] = []
        for s in rows:
            prob = s.get("problem") or {}
            contest_id = prob.get("contestId")
            index = prob.get("index")
            if contest_id is None or index is None:
                continue  # gym/acmsguru edge cases without a clean id
            ext = f"{contest_id}{index}"
            np = NormalizedProblem(
                platform="codeforces",
                external_id=ext,
                name=prob.get("name", ""),
                contest_id=contest_id,
                index=index,
                rating=prob.get("rating"),
                tags=prob.get("tags", []),
                url=f"https://codeforces.com/problemset/problem/{contest_id}/{index}",
            )
            out.append(
                NormalizedSubmission(
                    external_id=str(s["id"]),
                    verdict=s.get("verdict", "UNKNOWN"),
                    language=s.get("programmingLanguage", ""),
                    submitted_at=datetime.fromtimestamp(s["creationTimeSeconds"], tz=timezone.utc),
                    problem=np,
                )
            )
        return out
