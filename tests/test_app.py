"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store initial state
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Swimming Club": {
            "description": "Swimming training and water sports",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Studio": {
            "description": "Express creativity through painting and drawing",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Theater arts and performance training",
            "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Debate Team": {
            "description": "Learn public speaking and argumentation skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    
    # Clear and restore
    activities.clear()
    activities.update(initial_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) == 9

    def test_get_activities_includes_participant_info(self, client, reset_activities):
        """Test that activities include participant information"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "participants" in chess_club
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 2

    def test_get_activities_includes_all_details(self, client, reset_activities):
        """Test that activities include description, schedule, and max_participants"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball Team"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert activity["max_participants"] == 15


class TestSignupForActivity:
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=new@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "new@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Swimming%20Club/signup?email=test@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "test@mergington.edu" in data["Swimming Club"]["participants"]

    def test_signup_to_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signup to non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_duplicate_signup_fails(self, client, reset_activities):
        """Test that duplicate signup returns 400 error"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_increments_participant_count(self, client, reset_activities):
        """Test that signup increments the participant count"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Art Studio"]["participants"])
        
        # Signup
        client.post(
            "/activities/Art%20Studio/signup?email=artist@mergington.edu"
        )
        
        # Check new count
        response = client.get("/activities")
        new_count = len(response.json()["Art Studio"]["participants"])
        assert new_count == initial_count + 1

    def test_multiple_signups_for_different_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        student_email = "multi@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Drama%20Club/signup?email=" + student_email
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Science%20Club/signup?email=" + student_email
        )
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        data = response.json()
        assert student_email in data["Drama Club"]["participants"]
        assert student_email in data["Science Club"]["participants"]


class TestRootRedirect:
    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
