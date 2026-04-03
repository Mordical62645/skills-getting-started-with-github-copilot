import copy
from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_data(client):
    # Arrange (setup is in fixture)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "tester@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    unknown_activity = "NoSuchClub"

    # Act
    response = client.post(f"/activities/{unknown_activity}/signup", params={"email": "x@y.com"})

    # Assert
    assert response.status_code == 404


def test_remove_participant_success(client):
    # Arrange
    activity_name = "Chess Club"
    participant = activities[activity_name]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{participant}")

    # Assert
    assert response.status_code == 200
    assert participant not in activities[activity_name]["participants"]


def test_remove_unknown_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    bad_email = "never@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{bad_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
