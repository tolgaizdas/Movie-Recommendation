from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Movie Recommendation API is running!"}

def test_get_movies():
    response = client.get("/movies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Check if we get at least one movie (mock data)
    assert len(response.json()) > 0
    assert "title" in response.json()[0]

def test_recommendations_unauthorized():
    # Should fail without token
    response = client.post("/recommendations/", json={"user_id": "test", "num_recommendations": 5})
    assert response.status_code == 422

def test_recommendations_authorized_mock():
    # Test with mock token
    response = client.post(
        "/recommendations/", 
        json={"user_id": "test_user", "num_recommendations": 3},
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 3
