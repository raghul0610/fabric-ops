from uuid import uuid4
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.auth import AuthenticatedUser, get_current_user
from app.db import get_db
from app.main import app


client = TestClient(app)


def test_protected_route_requires_bearer_token() -> None:
    response = client.get("/events/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"


def test_authenticated_user_is_resolved_to_application_role() -> None:
    user_id = uuid4()
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "id": user_id,
        "role": "LEAD",
    }

    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=user_id)
    app.dependency_overrides[get_db] = lambda: db

    try:
        response = client.get("/events/me", headers={"Authorization": "Bearer test-token"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"user_id": str(user_id), "role": "LEAD"}


def test_authenticated_user_without_app_profile_is_forbidden() -> None:
    user_id = uuid4()
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = None

    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=user_id)
    app.dependency_overrides[get_db] = lambda: db

    try:
        response = client.get("/events/me", headers={"Authorization": "Bearer test-token"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Application user is not provisioned"
