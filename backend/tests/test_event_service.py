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
        self.members = set()

    def create(self, **kwargs):
        return self.event

    def list_all(self):
        return [self.event]

    def list_for_user(self, user_id):
        return [self.event] if user_id in self.members else []

    def get(self, event_id):
        return self.event if event_id == self.event["id"] else None

    def is_team_member_of_event(self, event_id, user_id):
        return event_id == self.event["id"] and user_id in self.members

    def update_state(self, event_id, state):
        self.event["state"] = state
        return self.event


def test_event_can_move_from_draft_to_planned_for_admin():
    repository = FakeRepository("DRAFT")
    service = EventService(repository)

    result = service.transition(
        repository.event["id"],
        "PLANNED",
        actor_id=uuid4(),
        actor_role="ADMIN",
    )

    assert result["state"] == "PLANNED"


def test_event_can_move_from_draft_to_planned_for_team_lead():
    repository = FakeRepository("DRAFT")
    lead = uuid4()
    repository.members.add(lead)
    service = EventService(repository)

    result = service.transition(
        repository.event["id"],
        "PLANNED",
        actor_id=lead,
        actor_role="LEAD",
    )

    assert result["state"] == "PLANNED"


def test_lead_cannot_change_unrelated_event():
    repository = FakeRepository("DRAFT")
    service = EventService(repository)

    with pytest.raises(Exception) as exc:
        service.transition(
            repository.event["id"],
            "PLANNED",
            actor_id=uuid4(),
            actor_role="LEAD",
        )

    assert exc.value.status_code == 403


def test_member_cannot_access_unrelated_event():
    repository = FakeRepository("DRAFT")
    service = EventService(repository)

    with pytest.raises(Exception) as exc:
        service.get(
            repository.event["id"],
            actor_id=uuid4(),
            actor_role="MEMBER",
        )

    assert exc.value.status_code == 403


def test_non_admin_event_listing_is_scoped():
    repository = FakeRepository()
    member = uuid4()
    service = EventService(repository)

    assert service.list_all(actor_id=member, actor_role="MEMBER") == []

    repository.members.add(member)
    assert service.list_all(actor_id=member, actor_role="MEMBER") == [repository.event]


def test_admin_event_listing_is_global():
    repository = FakeRepository()
    service = EventService(repository)

    assert service.list_all(actor_id=uuid4(), actor_role="ADMIN") == [repository.event]


def test_event_rejects_invalid_transition():
    repository = FakeRepository("DRAFT")
    service = EventService(repository)

    with pytest.raises(Exception) as exc:
        service.transition(
            repository.event["id"],
            "ACTIVE",
            actor_id=uuid4(),
            actor_role="ADMIN",
        )

    assert exc.value.status_code == 400


def test_event_cannot_move_after_completion():
    repository = FakeRepository("COMPLETED")
    service = EventService(repository)

    with pytest.raises(Exception) as exc:
        service.transition(
            repository.event["id"],
            "ACTIVE",
            actor_id=uuid4(),
            actor_role="ADMIN",
        )

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
