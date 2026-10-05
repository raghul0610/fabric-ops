from uuid import uuid4
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.auth import AuthenticatedUser, CurrentUser, get_current_app_user, get_current_user
from app.db import get_db
from app.main import app


client = TestClient(app)


def test_protected_route_requires_bearer_token() -> None:
    response = client.get("/events/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("post", "/events", {"name": "Unauthorized event"}),
        ("post", f"/events/{uuid4()}/teams", {"name": "Unauthorized team"}),
        (
            "post",
            f"/events/{uuid4()}/teams/{uuid4()}/tasks",
            {"title": "Unauthorized task"},
        ),
    ],
)
def test_protected_write_routes_require_authentication(
    method: str,
    path: str,
    payload: dict,
) -> None:
    response = getattr(client, method)(path, json=payload)
    assert response.status_code == 401


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


def test_database_failure_returns_service_unavailable_with_cors() -> None:
    user_id = uuid4()

    def unavailable_db():
        raise SQLAlchemyError("database unavailable")

    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=user_id)
    app.dependency_overrides[get_db] = unavailable_db

    try:
        response = client.get(
            "/events/me",
            headers={
                "Authorization": "Bearer test-token",
                "Origin": "http://localhost:5173",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"detail": "Database service unavailable"}
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_member_cannot_create_event() -> None:
    user_id = uuid4()
    app.dependency_overrides[get_current_app_user] = lambda: CurrentUser(
        id=user_id,
        role="MEMBER",
    )

    try:
        response = client.post("/events", json={"name": "Member event"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient role"


def test_member_cannot_review_submission() -> None:
    user_id = uuid4()
    app.dependency_overrides[get_current_app_user] = lambda: CurrentUser(
        id=user_id,
        role="MEMBER",
    )

    try:
        response = client.post(
            f"/submissions/{uuid4()}/reviews",
            json={"decision": "APPROVED"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient role"


def test_lead_cannot_create_event() -> None:
    user_id = uuid4()
    app.dependency_overrides[get_current_app_user] = lambda: CurrentUser(
        id=user_id,
        role="LEAD",
    )

    try:
        response = client.post("/events", json={"name": "Lead event"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient role"
