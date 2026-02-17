import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that all activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert "Drama Club" in data
        assert "Art Studio" in data
        assert "Debate Team" in data
        assert "Science Club" in data
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)
    
    def test_participants_list_contains_initial_data(self, client):
        """Test that participants list contains the initial data."""
        response = client.get("/activities")
        data = response.json()
        
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant for an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newemail@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newemail@mergington.edu" in data["message"]
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newemail@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_prevents_double_registration(self, client):
        """Test that signing up twice for the same activity is prevented."""
        email = "michael@mergington.edu"
        response = client.post(
            "/activities/Chess%20Club/signup?email=" + email
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity."""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_updates_participant_count(self, client):
        """Test that signup updates the participant count."""
        # Get initial count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()["Chess Club"]["participants"])
        
        # Sign up a new participant
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        
        # Get updated count
        activities_response = client.get("/activities")
        updated_count = len(activities_response.json()["Chess Club"]["participants"])
        
        assert updated_count == initial_count + 1
    
    def test_signup_multiple_different_activities(self, client):
        """Test signing up the same person to multiple activities."""
        email = "versatile@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant."""
        email = "michael@mergington.edu"
        response = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant not in the activity."""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notinlist@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity."""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_updates_participant_count(self, client):
        """Test that unregister updates the participant count."""
        email = "michael@mergington.edu"
        
        # Get initial count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()["Chess Club"]["participants"])
        
        # Unregister participant
        client.post(f"/activities/Chess%20Club/unregister?email={email}")
        
        # Get updated count
        activities_response = client.get("/activities")
        updated_count = len(activities_response.json()["Chess Club"]["participants"])
        
        assert updated_count == initial_count - 1
    
    def test_signup_after_unregister(self, client):
        """Test that a participant can sign up again after unregistering."""
        email = "michael@mergington.edu"
        
        # Unregister
        client.post(f"/activities/Chess%20Club/unregister?email={email}")
        
        # Verify they're not there
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Chess Club"]["participants"]
        
        # Sign up again
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response.status_code == 200
        
        # Verify they're back
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests for complex workflows."""
    
    def test_full_signup_and_unregister_flow(self, client):
        """Test a complete flow of getting activities, signing up, and unregistering."""
        email = "integration@mergington.edu"
        activity = "Debate Team"
        
        # Get activities
        response = client.get("/activities")
        assert response.status_code == 200
        initial_participants = len(response.json()[activity]["participants"])
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_participants + 1
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_participants
        assert email not in response.json()[activity]["participants"]
    
    def test_multiple_signups_and_unregisters(self, client):
        """Test multiple sequential signups and unregisters."""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        activity = "Art Studio"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up all students
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all are signed up
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count + 3
        for email in emails:
            assert email in response.json()[activity]["participants"]
        
        # Unregister all students
        for email in emails:
            response = client.post(f"/activities/{activity}/unregister?email={email}")
            assert response.status_code == 200
        
        # Verify all are unregistered
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count
        for email in emails:
            assert email not in response.json()[activity]["participants"]
