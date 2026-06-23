"""
Integration tests for FastAPI endpoints

Tests the GET /activities endpoint using the AAA (Arrange-Act-Assert) pattern.
"""

from fastapi.testclient import TestClient
from src.app import app


class TestActivityEndpoints:
    """Tests for /activities endpoint"""

    def test_get_all_activities_returns_200(self):
        """
        Arrange: Create a TestClient from the FastAPI app
        Act: Make a GET request to /activities
        Assert: Verify status code is 200
        """
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_all_activities_returns_non_empty_list(self):
        """
        Arrange: Create a TestClient
        Act: Get all activities
        Assert: Verify activities list is not empty
        """
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert len(activities) > 0

    def test_activities_have_required_fields(self):
        """
        Arrange: Create a TestClient and fetch activities
        Act: Parse the response and check each activity
        Assert: Verify each activity has required fields
        """
        # Arrange
        client = TestClient(app)
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str), f"Activity name should be string, got {type(activity_name)}"
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing field: {field}"

    def test_activities_participants_is_list(self):
        """
        Arrange: Create a TestClient
        Act: Get activities and check participants field
        Assert: Verify participants is a list for each activity
        """
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Activity {activity_name} participants should be a list"

    def test_activities_max_participants_is_positive_integer(self):
        """
        Arrange: Create a TestClient
        Act: Get activities and check max_participants field
        Assert: Verify max_participants is a positive integer for each activity
        """
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int), \
                f"Activity {activity_name} max_participants should be an integer"
            assert activity_data["max_participants"] > 0, \
                f"Activity {activity_name} max_participants should be positive"

    def test_specific_activity_chess_club_exists(self):
        """
        Arrange: Create a TestClient
        Act: Get activities and look for Chess Club
        Assert: Verify Chess Club exists in activities
        """
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert "Chess Club" in activities, "Chess Club should exist in activities"

    def test_specific_activity_has_valid_structure(self):
        """
        Arrange: Get all activities and select Chess Club
        Act: Examine the structure of Chess Club
        Assert: Verify it has all required fields with correct types
        """
        # Arrange
        client = TestClient(app)
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities.get("Chess Club")

        # Act & Assert
        assert chess_club is not None
        assert isinstance(chess_club["description"], str)
        assert isinstance(chess_club["schedule"], str)
        assert isinstance(chess_club["max_participants"], int)
        assert isinstance(chess_club["participants"], list)
