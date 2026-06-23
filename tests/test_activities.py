"""
Integration tests for activity signup/unregister workflows

Tests the POST /activities/{activity_name}/signup and POST /activities/{activity_name}/unregister
endpoints using the AAA (Arrange-Act-Assert) pattern.
"""

from fastapi.testclient import TestClient
from src.app import app


class TestActivitySignup:
    """Tests for signup and unregister workflows"""

    def test_signup_for_activity_returns_200(self):
        """
        Arrange: Create a TestClient and prepare signup data
        Act: Make a POST request to signup endpoint with valid activity and email
        Assert: Verify status code is 200
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Chess Club"
        email = "newstudent@test.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200

    def test_signup_returns_success_message(self):
        """
        Arrange: Create a TestClient with signup parameters
        Act: Sign up for an activity
        Assert: Verify response contains success message
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Programming Class"
        email = "programmer@test.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_increases_participant_count(self):
        """
        Arrange: Get initial participant count for an activity
        Act: Sign up a new student
        Assert: Verify participant count increased by 1
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Basketball"
        email = "baller@test.com"
        
        # Get initial participants
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - verify signup was successful
        assert signup_response.status_code == 200
        
        # Get updated participants
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        updated_count = len(updated_activities[activity_name]["participants"])
        
        assert updated_count == initial_count + 1

    def test_signup_for_nonexistent_activity_returns_404(self):
        """
        Arrange: Create a TestClient with non-existent activity name
        Act: Try to sign up for non-existent activity
        Assert: Verify status code is 404
        """
        # Arrange
        client = TestClient(app)
        fake_activity = "Fake Activity That Does Not Exist"
        email = "student@test.com"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email_returns_400(self):
        """
        Arrange: Sign up a student, then try to sign them up again
        Act: Make two signup requests with the same email
        Assert: Second request returns 400 status code
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Tennis"
        email = "duplicate@test.com"

        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200

        # Act - Try to sign up the same email again
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()


class TestActivityUnregister:
    """Tests for activity unregister functionality"""

    def test_unregister_from_activity_returns_200(self):
        """
        Arrange: Sign up for activity, then prepare to unregister
        Act: Make POST request to unregister endpoint
        Assert: Verify status code is 200
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Drama Club"
        email = "actor@test.com"
        
        # Sign up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200

    def test_unregister_returns_success_message(self):
        """
        Arrange: Sign up for activity
        Act: Unregister from activity
        Assert: Verify response contains success message
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Art Studio"
        email = "artist@test.com"
        
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_decreases_participant_count(self):
        """
        Arrange: Sign up for activity, get initial count
        Act: Unregister from activity
        Assert: Verify participant count decreased by 1
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Robotics Club"
        email = "roboticist@test.com"
        
        # Sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get count after signup
        response_after_signup = client.get("/activities")
        activities_after_signup = response_after_signup.json()
        count_after_signup = len(activities_after_signup[activity_name]["participants"])

        # Act
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert - verify unregister was successful
        assert unregister_response.status_code == 200
        
        # Get count after unregister
        response_after_unregister = client.get("/activities")
        activities_after_unregister = response_after_unregister.json()
        count_after_unregister = len(activities_after_unregister[activity_name]["participants"])
        
        assert count_after_unregister == count_after_signup - 1

    def test_unregister_non_participant_returns_400(self):
        """
        Arrange: Create a TestClient with email not signed up for activity
        Act: Try to unregister someone not signed up
        Assert: Verify status code is 400
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Debate Team"
        email = "notjoined@test.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_from_nonexistent_activity_returns_404(self):
        """
        Arrange: Create a TestClient with non-existent activity name
        Act: Try to unregister from non-existent activity
        Assert: Verify status code is 404
        """
        # Arrange
        client = TestClient(app)
        fake_activity = "Fake Activity"
        email = "student@test.com"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestActivityWorkflows:
    """Tests for complete signup/unregister workflows"""

    def test_complete_signup_unregister_workflow(self):
        """
        Arrange: Get initial state of an activity
        Act: Sign up, verify participation, then unregister
        Assert: Verify all state changes are correct
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Gym Class"
        email = "athlete@test.com"
        
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_count = len(initial_activities[activity_name]["participants"])
        initial_email_in_list = email in initial_activities[activity_name]["participants"]

        # Act 1 - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert signup was successful
        assert signup_response.status_code == 200

        # Check state after signup
        after_signup_response = client.get("/activities")
        after_signup_activities = after_signup_response.json()
        after_signup_count = len(after_signup_activities[activity_name]["participants"])
        after_signup_email_in_list = email in after_signup_activities[activity_name]["participants"]

        assert after_signup_count == initial_count + 1
        assert after_signup_email_in_list is True
        assert initial_email_in_list is False

        # Act 2 - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert unregister was successful
        assert unregister_response.status_code == 200

        # Check final state
        final_response = client.get("/activities")
        final_activities = final_response.json()
        final_count = len(final_activities[activity_name]["participants"])
        final_email_in_list = email in final_activities[activity_name]["participants"]

        assert final_count == initial_count
        assert final_email_in_list is False

    def test_multiple_students_signup_for_same_activity(self):
        """
        Arrange: Get initial participant count
        Act: Sign up multiple different students
        Assert: Verify participant count increased for each signup
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Programming Class"
        emails = ["student1@test.com", "student2@test.com", "student3@test.com"]
        
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act & Assert
        for idx, email in enumerate(emails):
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
            
            # Verify count after each signup
            current_response = client.get("/activities")
            current_count = len(current_response.json()[activity_name]["participants"])
            assert current_count == initial_count + idx + 1
