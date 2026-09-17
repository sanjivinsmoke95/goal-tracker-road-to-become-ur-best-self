from datetime import datetime, timezone

from app.api.deps import get_lc_adapter
from app.main import app
from app.services.adapters.base import NormalizedProblem, NormalizedProfile, NormalizedSubmission
from tests.conftest import register_and_login


class FakeLC:
    platform = "leetcode"

    def fetch_profile(self, handle):
        return NormalizedProfile(handle=handle)

    def fetch_submissions(self, handle):
        return [
            NormalizedSubmission(
                external_id="s1", verdict="OK", language="",
                submitted_at=datetime(2026, 9, 10, tzinfo=timezone.utc),
                problem=NormalizedProblem(platform="leetcode", external_id="two-sum", name="Two Sum",
                                          url="https://leetcode.com/problems/two-sum/"),
            )
        ]


def test_connect_seeds_corpus_and_ingests(client):
    h = register_and_login(client)
    app.dependency_overrides[get_lc_adapter] = lambda: FakeLC()
    r = client.post("/platforms/leetcode/connect", json={"handle": "alice"}, headers=h)
    assert r.status_code == 200
    assert r.json()["new_submissions"] == 1

    profile = client.get("/leetcode/profile", headers=h).json()
    assert profile["connected"] is True
    assert profile["solved"] == 1

    # The seed corpus gives unsolved candidates → a LeetCode POTD exists.
    lc = client.get("/problems/today", headers=h).json()["leetcode"]
    assert lc is not None
    assert lc["problem"]["platform"] == "leetcode"
    assert lc["problem"]["id"] != "le:two-sum"  # never the solved one


def test_manual_import(client):
    h = register_and_login(client)
    r = client.post("/platforms/leetcode/import", json={"items": [
        {"slug": "3sum", "title": "3Sum", "difficulty": "Medium", "tags": ["array"]},
    ]}, headers=h)
    assert r.status_code == 200
    assert r.json()["new_solved"] == 1
    solved = client.get("/leetcode/problems?solved=true", headers=h).json()
    assert "3sum" in {p["external_id"] for p in solved}
