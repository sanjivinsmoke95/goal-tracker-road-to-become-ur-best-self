from datetime import datetime, timezone

from app.api.deps import get_cf_adapter
from app.main import app
from app.services.adapters.base import NormalizedProblem, NormalizedProfile, NormalizedSubmission
from tests.conftest import register_and_login


def _sub(i, ext, rating, tags, verdict):
    return NormalizedSubmission(
        external_id=str(i), verdict=verdict, language="c++",
        submitted_at=datetime(2026, 9, 10, tzinfo=timezone.utc),
        problem=NormalizedProblem(platform="codeforces", external_id=ext, name=f"P{ext}",
                                  contest_id=int(ext[:-1]), index=ext[-1], rating=rating, tags=tags,
                                  url=f"https://cf/{ext}"),
    )


class FakeAdapter:
    platform = "codeforces"

    def __init__(self, subs, corpus):
        self._subs = subs
        self._corpus = corpus

    def fetch_profile(self, handle):
        return NormalizedProfile(handle=handle, rating=1000)

    def fetch_submissions(self, handle):
        return list(self._subs)

    def fetch_problemset(self):
        return list(self._corpus)


def _corpus():
    # A spread of unsolved problems so the engine has candidates near ~900-1000.
    out = []
    for cid, rating, tags in [
        (2001, 800, ["implementation"]),
        (2002, 900, ["greedy"]),
        (2003, 1000, ["dp"]),
        (2004, 1100, ["graphs"]),
        (2005, 1500, ["dp"]),
    ]:
        out.append(NormalizedProblem(platform="codeforces", external_id=f"{cid}A", name=f"C{cid}",
                                     contest_id=cid, index="A", rating=rating, tags=tags, url=f"https://cf/{cid}A"))
    return out


def test_problem_of_the_day_is_deterministic_and_explained(client):
    h = register_and_login(client)
    solved = [_sub(i, f"150{i}A", 900, ["greedy"], "OK") for i in range(6)]
    app.dependency_overrides[get_cf_adapter] = lambda: FakeAdapter(solved, _corpus())
    client.post("/platforms/codeforces/connect", json={"handle": "x"}, headers=h)

    r = client.get("/problems/today", headers=h)
    assert r.status_code == 200
    cf = r.json()["codeforces"]
    assert cf is not None
    # A real, unsolved problem near the recommended level, with an explanation.
    assert cf["problem"]["rating"] is not None
    assert cf["explanation"]  # non-empty (stub explanation)
    assert "difficulty_fit" in cf["reason"]["components"]

    # Idempotent within the day: asking again returns the same problem.
    again = client.get("/problems/today", headers=h).json()["codeforces"]
    assert again["problem"]["id"] == cf["problem"]["id"]


def test_potd_never_recommends_solved(client):
    h = register_and_login(client)
    # Solve everything at 900-1000 except leave 2004/1100 unsolved.
    solved = [
        _sub(1, "2002A", 900, ["greedy"], "OK"),
        _sub(2, "2003A", 1000, ["dp"], "OK"),
    ]
    app.dependency_overrides[get_cf_adapter] = lambda: FakeAdapter(solved, _corpus())
    client.post("/platforms/codeforces/connect", json={"handle": "x"}, headers=h)
    cf = client.get("/problems/today", headers=h).json()["codeforces"]
    assert cf is not None
    assert cf["problem"]["id"] not in {"co:2002A", "co:2003A"}
