from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_delete_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "student@example.com"

    activities[activity_name]["participants"].append(email)

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert "Removed" in response.json()["message"]


def test_delete_participant_returns_404_when_email_not_found():
    activity_name = "Programming Class"
    email = "not-registered@example.com"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"
