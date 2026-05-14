from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_list():
    # Arrange
    expected_keys = set(activities.keys())

    # Act
    response = client.get("/activities")
    response_data = response.json()

    # Assert
    assert response.status_code == 200
    assert set(response_data.keys()) == expected_keys
    assert all("description" in activity for activity in response_data.values())
    assert all("participants" in activity for activity in response_data.values())


def test_unregister_from_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "test-student@example.com"
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "ghost@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up_student_returns_400():
    # Arrange
    activity_name = "Programming Class"
    email = "not-signed-up@example.com"
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"
