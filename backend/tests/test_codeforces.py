from datetime import datetime, timezone

from app.api.deps import get_cf_adapter
from app.main import app
from app.services.adapters.base import (
    NormalizedProblem,
    NormalizedProfile,
    NormalizedSubmission,
)
from tests.conftest import register_and_login


def _sub(sub_id, ext, rating, tags, verdict, day):
    return NormalizedSubmission(
        external_id=str(sub_id),
        verdict=verdict,
        language="GNU C++17",
        submitted_at=datetime(2026, 9, day, tzinfo=timezone.utc),
        problem=NormalizedProblem(
            platform="codeforces",
            external_id=ext,
            name=f"Problem {ext}",
            contest_id=int(ext[:-1]),
            index=ext[-1],
            rating=rating,
            tags=tags,
            url=f"https://codeforces.com/problemset/problem/{ext[:-1]}/{ext[-1]}",
        ),
    )


class FakeAdapter:
    platform = "codeforces"

    def __init__(self, subs):
        self._subs = subs

    def fetch_profile(self, handle):
        return NormalizedProfile(handle=handle, rating=1234, max_rating=1400, rank="pupil", max_rank="specialist")

    def fetch_submissions(self, handle):
        return list(self._subs)


def _use_adapter(subs):
    app.dependency_overrides[get_cf_adapter] = lambda: FakeAdapter(subs)


def test_connect_ingests_profile_and_submissions(client):
    h = register_and_login(client)
    _use_adapter([
        _sub(1, "1500A", 800, ["implementation"], "OK", 1),
        _sub(2, "1500B", 900, ["greedy"], "WRONG_ANSWER", 2),
    ])
    r = client.post("/platforms/codeforces/connect", json={"handle": "tourist"}, headers=h)
    assert r.status_code == 200
    assert r.json()["rating"] == 1234
    assert r.json()["rank"] == "pupil"

    subs = client.get("/codeforces/submissions", headers=h).json()
    assert len(subs) == 2
    assert subs[0]["source_available"] is False  # CF API gives no source


def test_sync_counts_new_and_solved(client):
    h = register_and_login(client)
    _use_adapter([_sub(1, "1500A", 800, ["implementation"], "OK", 1)])
    client.post("/platforms/codeforces/connect", json={"handle": "x"}, headers=h)

    # Re-sync with an additional new accepted submission.
    _use_adapter([
        _sub(1, "1500A", 800, ["implementation"], "OK", 1),
        _sub(2, "1600C", 1000, ["dp"], "OK", 3),
    ])
    r = client.post("/platforms/codeforces/sync", headers=h)
    body = r.json()
    assert body["new_submissions"] == 1
    assert body["new_solved"] == 1


def test_problems_solved_filter(client):
    h = register_and_login(client)
    _use_adapter([
        _sub(1, "1500A", 800, ["implementation"], "OK", 1),
        _sub(2, "1500B", 900, ["greedy"], "WRONG_ANSWER", 2),
    ])
    client.post("/platforms/codeforces/connect", json={"handle": "x"}, headers=h)

    solved = client.get("/codeforces/problems?solved=true", headers=h).json()
    assert {p["external_id"] for p in solved} == {"1500A"}
    unsolved = client.get("/codeforces/problems?solved=false", headers=h).json()
    assert "1500B" in {p["external_id"] for p in unsolved}


def test_sync_requires_connection_first(client):
    h = register_and_login(client)
    assert client.post("/platforms/codeforces/sync", headers=h).status_code == 400


def test_switching_handle_resets_submissions(client):
    h = register_and_login(client)
    _use_adapter([_sub(1, "1500A", 800, ["impl"], "OK", 1), _sub(2, "1600B", 2000, ["dp"], "OK", 2)])
    client.post("/platforms/codeforces/connect", json={"handle": "strongcoder"}, headers=h)
    assert len(client.get("/codeforces/submissions", headers=h).json()) == 2

    # Connect a DIFFERENT handle → the previous person's submissions must be gone.
    _use_adapter([_sub(9, "1000A", 800, ["impl"], "OK", 3)])
    client.post("/platforms/codeforces/connect", json={"handle": "newbie"}, headers=h)
    subs = client.get("/codeforces/submissions", headers=h).json()
    assert len(subs) == 1
    assert subs[0]["external_id"] == "9"
