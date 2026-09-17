from datetime import datetime, timezone

from app.api.deps import get_cf_adapter
from app.main import app
from app.services.adapters.base import NormalizedProblem, NormalizedProfile, NormalizedSubmission
from tests.conftest import register_and_login


class FakeAdapter:
    platform = "codeforces"

    def fetch_profile(self, handle):
        return NormalizedProfile(handle=handle, rating=1000)

    def fetch_submissions(self, handle):
        return [
            NormalizedSubmission(
                external_id="101", verdict="OK", language="GNU C++17",
                submitted_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
                problem=NormalizedProblem(
                    platform="codeforces", external_id="1500A", name="P", contest_id=1500,
                    index="A", rating=900, tags=["greedy"], url="https://cf/1500A"),
            )
        ]


def _connect(client, headers):
    app.dependency_overrides[get_cf_adapter] = lambda: FakeAdapter()
    client.post("/platforms/codeforces/connect", json={"handle": "x"}, headers=headers)
    return client.get("/codeforces/submissions", headers=headers).json()[0]["id"]


def test_analyze_records_mistakes(client):
    h = register_and_login(client)
    sid = _connect(client, h)
    # Code with a nested loop + int*int → stub heuristics flag O(n^2) + overflow.
    code = "for(int i=0;i<n;i++){ for(int j=0;j<n;j++){ int x = a*b; }}"
    r = client.post(f"/submissions/{sid}/analyze", json={"code": code, "language": "GNU C++17"}, headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["correctness"] == "Accepted"
    types = {m["mistake_type"] for m in body["mistakes"]}
    assert "unnecessary_on2" in types
    assert "integer_overflow" in types


def test_mistakes_aggregate_recurring(client):
    h = register_and_login(client)
    sid = _connect(client, h)
    code = "for (a) { for (b) { int x = a * b; } }"
    for _ in range(3):
        client.post(f"/submissions/{sid}/analyze", json={"code": code, "language": "GNU C++17"}, headers=h)
    mistakes = client.get("/mistakes", headers=h).json()
    by_type = {m["mistake_type"]: m for m in mistakes}
    assert by_type["unnecessary_on2"]["frequency"] == 3
    assert by_type["integer_overflow"]["severity"] == "high"


def test_submission_detail_includes_problem(client):
    h = register_and_login(client)
    sid = _connect(client, h)
    d = client.get(f"/submissions/{sid}", headers=h).json()
    assert d["problem"]["rating"] == 900
    assert d["submission"]["verdict"] == "OK"
