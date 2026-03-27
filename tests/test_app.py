from src.app import activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data_and_no_store_cache_header(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"

    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["schedule"] == activities["Chess Club"]["schedule"]
    assert "participants" in payload["Chess Club"]


def test_signup_adds_new_participant(client):
    new_email = "new.student@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": new_email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for Chess Club"}
    assert new_email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    existing_email = activities["Chess Club"]["participants"][0]

    response = client.post("/activities/Chess%20Club/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert response.json() == {"detail": "Already signed up for this activity"}


def test_signup_rejects_missing_activity(client):
    response = client.post("/activities/Robotics%20Team/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_full_activity(client, activities_state):
    activities_state["Chess Club"]["participants"] = [
        f"student{index}@mergington.edu" for index in range(activities_state["Chess Club"]["max_participants"])
    ]

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "late.student@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}


def test_unregister_removes_existing_participant(client):
    existing_email = activities["Tennis Club"]["participants"][0]

    response = client.delete(
        "/activities/Tennis%20Club/participants",
        params={"email": existing_email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {existing_email} from Tennis Club"}
    assert existing_email not in activities["Tennis Club"]["participants"]


def test_unregister_rejects_missing_participant(client):
    response = client.delete(
        "/activities/Tennis%20Club/participants",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found for this activity"}


def test_unregister_rejects_missing_activity(client):
    response = client.delete(
        "/activities/Robotics%20Team/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}