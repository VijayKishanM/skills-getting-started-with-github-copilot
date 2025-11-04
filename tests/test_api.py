import uuid
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Basic sanity: at least one known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = f"test_{uuid.uuid4().hex}@example.com"

    # get current participants count
    resp = client.get("/activities")
    assert resp.status_code == 200
    before = resp.json()
    before_count = len(before[activity]["participants"]) if activity in before else 0

    # sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # verify added
    resp = client.get("/activities")
    assert resp.status_code == 200
    after = resp.json()
    assert email in after[activity]["participants"]
    assert len(after[activity]["participants"]) == before_count + 1

    # unregister
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # verify removed
    resp = client.get("/activities")
    assert resp.status_code == 200
    final = resp.json()
    assert email not in final[activity]["participants"]
    assert len(final[activity]["participants"]) == before_count
