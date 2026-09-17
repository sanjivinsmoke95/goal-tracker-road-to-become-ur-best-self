from datetime import date, timedelta

from app.services.plan_service import parse_upload, rebalance
from tests.conftest import register_and_login

CSV = b"Day,Category,Topic,Task,Duration\n1,CF,Greedy,Solve 2 problems,90\n1,React,JSX,Learn JSX,60\n2,Backend,REST,Learn REST,60\n"
JSON = b'[{"day":1,"tasks":[{"category":"cf","title":"Solve 2 problems"},{"category":"react","title":"JSX"}]}]'


def test_parse_csv_groups_by_day():
    days = parse_upload(CSV, "plan.csv")
    assert [d["day"] for d in days] == [1, 2]
    assert len(days[0]["tasks"]) == 2
    assert days[0]["tasks"][0]["category"] == "cf"


def test_parse_json():
    days = parse_upload(JSON, "plan.json")
    assert len(days[0]["tasks"]) == 2


def test_rebalance_moves_overdue_undone_forward():
    today = date(2026, 9, 17)
    days = [
        {"date": today - timedelta(days=1), "tasks": [{"title": "a", "done": False}, {"title": "b", "done": True}]},
        {"date": today, "tasks": [{"title": "c", "done": False}]},
        {"date": today + timedelta(days=1), "tasks": []},
    ]
    rebalance(days, today)
    # 'a' (undone, overdue) moved forward; 'b' (done) stays as history.
    assert days[0]["tasks"] == [{"title": "b", "done": True}]
    future_titles = days[1]["tasks"] + days[2]["tasks"]
    assert any(t["title"] == "a" for t in future_titles)


def test_upload_endpoint_creates_plan(client):
    h = register_and_login(client)
    r = client.post("/plans/upload", files={"file": ("plan.csv", CSV, "text/csv")}, headers=h)
    assert r.status_code == 200
    plan = r.json()
    assert plan["source"] == "upload"
    assert len(plan["days"]) == 2
    current = client.get("/plans/current", headers=h).json()
    assert current["id"] == plan["id"]


def test_generate_endpoint(client):
    h = register_and_login(client)
    r = client.post("/plans/generate", json={"goal": "Learn React + DSA", "duration_days": 5, "hours_per_day": 3}, headers=h)
    assert r.status_code == 200
    assert len(r.json()["days"]) == 5


def test_adapt_endpoint(client):
    h = register_and_login(client)
    plan = client.post("/plans/generate", json={"goal": "x", "duration_days": 3, "hours_per_day": 2}, headers=h).json()
    r = client.post(f"/plans/{plan['id']}/adapt", headers=h)
    assert r.status_code == 200
    assert "redistributed_tasks" in r.json()
