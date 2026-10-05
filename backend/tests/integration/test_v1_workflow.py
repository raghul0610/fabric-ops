import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db import engine
from app.main import app


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

ROLE_CREDENTIALS = {
    "admin": (
        os.getenv("FABRIC_ADMIN_EMAIL"),
        os.getenv("FABRIC_ADMIN_PASSWORD"),
    ),
    "lead": (
        os.getenv("FABRIC_LEAD_EMAIL"),
        os.getenv("FABRIC_LEAD_PASSWORD"),
    ),
    "member": (
        os.getenv("FABRIC_MEMBER_EMAIL"),
        os.getenv("FABRIC_MEMBER_PASSWORD"),
    ),
}


def _missing_configuration() -> list[str]:
    missing = [
        name
        for name, value in {
            "SUPABASE_URL": SUPABASE_URL,
            "SUPABASE_PUBLISHABLE_KEY": SUPABASE_PUBLISHABLE_KEY,
            "DATABASE_URL": DATABASE_URL,
        }.items()
        if not value
    ]
    for role, (email, password) in ROLE_CREDENTIALS.items():
        if not email:
            missing.append(f"FABRIC_{role.upper()}_EMAIL")
        if not password:
            missing.append(f"FABRIC_{role.upper()}_PASSWORD")
    return missing


def _login(email: str, password: str) -> str:
    response = httpx.post(
        f"{SUPABASE_URL.rstrip('/')}/auth/v1/token?grant_type=password",
        headers={
            "apikey": SUPABASE_PUBLISHABLE_KEY,
            "Content-Type": "application/json",
        },
        json={"email": email, "password": password},
        timeout=10,
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _skip_if_dependencies_unavailable() -> None:
    try:
        httpx.get(
            f"{SUPABASE_URL.rstrip('/')}/auth/v1/settings",
            headers={"apikey": SUPABASE_PUBLISHABLE_KEY},
            timeout=5,
        )
    except httpx.RequestError as exc:
        pytest.skip(f"Supabase is unavailable: {exc}")

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        pytest.skip(f"Database is unavailable: {exc}")


@pytest.mark.integration
def test_v1_admin_to_member_to_review_workflow() -> None:
    missing = _missing_configuration()
    if missing:
        pytest.skip(
            "V1 integration workflow requires environment variables: "
            + ", ".join(missing)
        )

    _skip_if_dependencies_unavailable()

    admin_email, admin_password = ROLE_CREDENTIALS["admin"]
    lead_email, lead_password = ROLE_CREDENTIALS["lead"]
    member_email, member_password = ROLE_CREDENTIALS["member"]

    admin_token = _login(admin_email, admin_password)
    lead_token = _login(lead_email, lead_password)
    member_token = _login(member_email, member_password)

    client = TestClient(app)

    admin_me = client.get("/events/me", headers=_headers(admin_token))
    lead_me = client.get("/events/me", headers=_headers(lead_token))
    member_me = client.get("/events/me", headers=_headers(member_token))

    assert admin_me.status_code == 200, admin_me.text
    assert lead_me.status_code == 200, lead_me.text
    assert member_me.status_code == 200, member_me.text
    assert admin_me.json()["role"] == "ADMIN"
    assert lead_me.json()["role"] == "LEAD"
    assert member_me.json()["role"] == "MEMBER"

    admin_id = admin_me.json()["user_id"]
    lead_id = lead_me.json()["user_id"]
    member_id = member_me.json()["user_id"]

    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = start + timedelta(hours=2)

    event_response = client.post(
        "/events",
        headers=_headers(admin_token),
        json={
            "name": "FABRIC V1 Acceptance",
            "description": "Automated end-to-end acceptance workflow",
            "starts_at": start.isoformat(),
            "ends_at": end.isoformat(),
        },
    )
    assert event_response.status_code == 201, event_response.text
    event_id = event_response.json()["id"]
    assert event_response.json()["state"] == "DRAFT"

    for state in ("PLANNED", "ACTIVE"):
        response = client.patch(
            f"/events/{event_id}/state",
            headers=_headers(admin_token),
            json={"state": state},
        )
        assert response.status_code == 200, response.text
        assert response.json()["state"] == state

    team_response = client.post(
        f"/events/{event_id}/teams",
        headers=_headers(admin_token),
        json={"name": "V1 Acceptance Team"},
    )
    assert team_response.status_code == 201, team_response.text
    team_id = team_response.json()["id"]

    lead_membership = client.post(
        f"/teams/{team_id}/members",
        headers=_headers(admin_token),
        json={"user_id": lead_id, "membership_role": "LEAD"},
    )
    assert lead_membership.status_code == 201, lead_membership.text

    member_membership = client.post(
        f"/teams/{team_id}/members",
        headers=_headers(admin_token),
        json={"user_id": member_id, "membership_role": "MEMBER"},
    )
    assert member_membership.status_code == 201, member_membership.text

    task_response = client.post(
        f"/events/{event_id}/teams/{team_id}/tasks",
        headers=_headers(lead_token),
        json={
            "title": "Complete acceptance task",
            "description": "Submit a V1 acceptance artifact",
            "assignee_id": member_id,
        },
    )
    assert task_response.status_code == 201, task_response.text
    task_id = task_response.json()["id"]
    assert task_response.json()["state"] == "TODO"

    start_task = client.patch(
        f"/tasks/{task_id}/state",
        headers=_headers(member_token),
        json={"state": "IN_PROGRESS"},
    )
    assert start_task.status_code == 200, start_task.text
    assert start_task.json()["state"] == "IN_PROGRESS"

    submission_response = client.post(
        f"/tasks/{task_id}/submissions",
        headers=_headers(member_token),
        json={"content": "FABRIC V1 acceptance artifact"},
    )
    assert submission_response.status_code == 201, submission_response.text
    submission_id = submission_response.json()["id"]

    task_after_submission = client.get(
        f"/tasks/{task_id}",
        headers=_headers(member_token),
    )
    assert task_after_submission.status_code == 200, task_after_submission.text
    assert task_after_submission.json()["state"] == "SUBMITTED"

    lead_submission = client.get(
        f"/submissions/{submission_id}",
        headers=_headers(lead_token),
    )
    assert lead_submission.status_code == 200, lead_submission.text

    review_response = client.post(
        f"/submissions/{submission_id}/reviews",
        headers=_headers(lead_token),
        json={
            "decision": "APPROVED",
            "feedback": "V1 acceptance passed",
        },
    )
    assert review_response.status_code == 201, review_response.text

    final_task = client.get(
        f"/tasks/{task_id}",
        headers=_headers(member_token),
    )
    assert final_task.status_code == 200, final_task.text
    assert final_task.json()["state"] == "APPROVED"

    completed_event = client.patch(
        f"/events/{event_id}/state",
        headers=_headers(admin_token),
        json={"state": "COMPLETED"},
    )
    assert completed_event.status_code == 200, completed_event.text
    assert completed_event.json()["state"] == "COMPLETED"

    assert admin_id
