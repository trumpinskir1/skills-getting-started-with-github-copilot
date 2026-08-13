from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset the in-memory activity store before each test."""
    original_state = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_state))


def test_get_activities_returns_activity_data(reset_activities):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert payload[expected_activity]["max_participants"] == 12
    assert "michael@mergington.edu" in payload[expected_activity]["participants"]


def test_signup_for_activity_adds_student(reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "new-student@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_returns_400_for_duplicate_email(reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_activity_returns_404_for_missing_activity(reset_activities):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_removes_email_from_activity(reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "student@example.com"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert "Removed" in response.json()["message"]


def test_delete_participant_returns_404_when_email_not_found(reset_activities):
    # Arrange
    activity_name = "Programming Class"
    email = "not-registered@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"


def test_delete_participant_returns_404_for_missing_activity(reset_activities):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
