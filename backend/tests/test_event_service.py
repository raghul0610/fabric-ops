from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.services.event_service import EventService


class FakeRepository:
    def __init__(self, state="DRAFT"):
        self.event = {
            "id": uuid4(),
            "name": "FABRIC",
            "description": "Event",
            "state": state,
            "starts_at": datetime(2026, 10, 10, 10, 0),
            "ends_at": datetime(2026, 10, 10, 12, 0),
            "created_at": datetime(2026, 10, 1, 10, 0),
            "updated_at": datetime(2026, 10, 1, 10, 0),
        }

    def create(self, **kwargs):
        return self.event

    def list_all(self):
        return [self.event]

    def get(self, event_id):
        return self.event

    def update_state(self, event_id, state):
        self.event["state"] = state
        return self.event


def test_event_can_move_from_draft_to_planned():
    repository = FakeRepository("DRAFT")
    service = EventService(repository)

    result = service.transition(repository.event["id"], "PLANNED")

    assert result["state"] == "PLANNED"


def test_event_rejects_invalid_transition():
    repository = FakeRepository("DRAFT")
    service = EventService(repository)

    with pytest.raises(Exception) as exc:
        service.transition(repository.event["id"], "ACTIVE")

    assert exc.value.status_code == 400


def test_event_cannot_move_after_completion():
    repository = FakeRepository("COMPLETED")
    service = EventService(repository)

    with pytest.raises(Exception) as exc:
        service.transition(repository.event["id"], "ACTIVE")

    assert exc.value.status_code == 400


def test_event_rejects_end_before_start():
    repository = FakeRepository()
    service = EventService(repository)
    start = datetime(2026, 10, 10, 12, 0)
    end = start - timedelta(minutes=1)

    with pytest.raises(Exception) as exc:
        service.create(
            name="Invalid",
            description=None,
            starts_at=start,
            ends_at=end,
        )

    assert exc.value.status_code == 400
