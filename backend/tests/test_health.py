from fastapi.testclient import TestClient

from app.main import app
from app.routers.health import database_health


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "fabric-ops-api"


def test_database_health() -> None:
    class FakeDb:
        def execute(self, query) -> None:
            return None

    assert database_health(FakeDb()) == {
        "status": "ok",
        "database": "reachable",
    }
