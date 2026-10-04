import os

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")
TEST_EMAIL = os.getenv("FABRIC_TEST_EMAIL")
TEST_PASSWORD = os.getenv("FABRIC_TEST_PASSWORD")


@pytest.mark.integration
def test_supabase_auth_to_fastapi() -> None:
    missing = [
        name
        for name, value in {
            "SUPABASE_URL": SUPABASE_URL,
            "SUPABASE_PUBLISHABLE_KEY": SUPABASE_PUBLISHABLE_KEY,
            "FABRIC_TEST_EMAIL": TEST_EMAIL,
            "FABRIC_TEST_PASSWORD": TEST_PASSWORD,
        }.items()
        if not value
    ]
    if missing:
        pytest.fail(
            "Missing integration-test environment variables: "
            + ", ".join(missing)
        )

    login_response = httpx.post(
        f"{SUPABASE_URL.rstrip('/')}/auth/v1/token?grant_type=password",
        headers={
            "apikey": SUPABASE_PUBLISHABLE_KEY,
            "Content-Type": "application/json",
        },
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
        timeout=10,
    )
    assert login_response.status_code == 200, login_response.text

    access_token = login_response.json()["access_token"]

    client = TestClient(app)
    response = client.get(
        "/events/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user_id"]
    assert body["role"] == "ADMIN"
