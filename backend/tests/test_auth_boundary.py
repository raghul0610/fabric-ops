from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_protected_route_requires_bearer_token() -> None:
    response = client.get("/events/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"
