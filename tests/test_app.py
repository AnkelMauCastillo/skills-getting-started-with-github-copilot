from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture()
def client():
    original_activities = deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert body["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant(client):
    # Arrange
    signup_url = "/activities/Chess%20Club/signup?email=student@mergington.edu"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up student@mergington.edu for Chess Club"}
    assert "student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    signup_url = "/activities/Chess%20Club/signup?email=michael@mergington.edu"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    signup_url = "/activities/Unknown%20Club/signup?email=student@mergington.edu"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    unregister_url = "/activities/Chess%20Club/signup?email=michael@mergington.edu"

    # Act
    response = client.delete(unregister_url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Removed michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_returns_404_when_participant_missing(client):
    # Arrange
    unregister_url = "/activities/Chess%20Club/signup?email=missing@mergington.edu"

    # Act
    response = client.delete(unregister_url)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student not signed up for this activity"}


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    unregister_url = "/activities/Unknown%20Club/signup?email=student@mergington.edu"

    # Act
    response = client.delete(unregister_url)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}