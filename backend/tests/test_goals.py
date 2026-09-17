from datetime import date, timedelta

from app.services.goals_service import compute_streak
from tests.conftest import register_and_login


# ---- pure streak logic (no DB) ----

def test_streak_empty():
    assert compute_streak(set(), date(2026, 9, 17)) == 0


def test_streak_counts_consecutive_including_today():
    today = date(2026, 9, 17)
    dates = {today, today - timedelta(days=1), today - timedelta(days=2)}
    assert compute_streak(dates, today) == 3


def test_streak_grace_when_today_empty_but_yesterday_done():
    today = date(2026, 9, 17)
    dates = {today - timedelta(days=1), today - timedelta(days=2)}
    assert compute_streak(dates, today) == 2  # not broken until today ends


def test_streak_breaks_on_gap():
    today = date(2026, 9, 17)
    dates = {today, today - timedelta(days=2)}  # missed yesterday
    assert compute_streak(dates, today) == 1


def test_streak_zero_when_stale():
    today = date(2026, 9, 17)
    dates = {today - timedelta(days=3)}
    assert compute_streak(dates, today) == 0


# ---- API ----

def test_create_and_list_goal(client):
    h = register_and_login(client)
    r = client.post("/goals", json={"title": "Solve CF problem", "category": "cf", "priority": "high"}, headers=h)
    assert r.status_code == 201
    goal = r.json()
    assert goal["title"] == "Solve CF problem"
    assert goal["status"] == "pending"
    assert goal["date"] == date.today().isoformat()

    r = client.get("/goals", headers=h)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_toggle_complete_updates_streak(client):
    h = register_and_login(client)
    gid = client.post("/goals", json={"title": "React useState", "category": "react"}, headers=h).json()["id"]

    # streak starts at 0
    assert client.get("/goals/streak", headers=h).json()["streak"] == 0

    # complete it
    r = client.post(f"/goals/{gid}/complete", headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
    assert r.json()["completed_at"] is not None

    s = client.get("/goals/streak", headers=h).json()
    assert s["streak"] == 1 and s["today_completed"] == 1 and s["today_total"] == 1

    # un-complete (toggle back)
    r = client.post(f"/goals/{gid}/complete", headers=h)
    assert r.json()["status"] == "pending"
    assert client.get("/goals/streak", headers=h).json()["streak"] == 0


def test_patch_status(client):
    h = register_and_login(client)
    gid = client.post("/goals", json={"title": "Backend REST"}, headers=h).json()["id"]
    r = client.patch(f"/goals/{gid}", json={"status": "in_progress", "notes": "reading docs"}, headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"
    assert r.json()["notes"] == "reading docs"


def test_delete_goal(client):
    h = register_and_login(client)
    gid = client.post("/goals", json={"title": "temp"}, headers=h).json()["id"]
    assert client.delete(f"/goals/{gid}", headers=h).status_code == 204
    assert client.get("/goals", headers=h).json() == []


def test_goals_require_auth(client):
    assert client.get("/goals").status_code in (401, 403)


def test_cannot_touch_another_users_goal(client):
    h1 = register_and_login(client, email="one@x.com")
    gid = client.post("/goals", json={"title": "mine"}, headers=h1).json()["id"]
    h2 = register_and_login(client, email="two@x.com")
    assert client.patch(f"/goals/{gid}", json={"status": "completed"}, headers=h2).status_code == 404


def test_dashboard_reflects_goals(client):
    h = register_and_login(client)
    client.post("/goals", json={"title": "Solve LC problem", "category": "lc"}, headers=h)
    body = client.get("/dashboard", headers=h).json()
    assert len(body["today_goals"]) == 1
    assert body["today_goals"][0]["title"] == "Solve LC problem"
    assert body["streak"] == 0
