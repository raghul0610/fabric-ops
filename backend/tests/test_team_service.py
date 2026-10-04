from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services.team_service import TeamService


class FakeRepository:
    def __init__(self):
        self.teams = {}
        self.members = set()
        self.db = type("DB", (), {"rollback": lambda self: None})()

    def event_exists(self, event_id):
        return True

    def team_name_exists(self, event_id, name):
        return any(
            team["event_id"] == event_id and team["name"] == name
            for team in self.teams.values()
        )

    def create(self, **kwargs):
        team = {
            "id": uuid4(),
            "event_id": kwargs["event_id"],
            "name": kwargs["name"],
            "created_at": None,
        }
        self.teams[team["id"]] = team
        return team

    def get(self, team_id):
        return self.teams.get(team_id)

    def list_for_event(self, event_id, **kwargs):
        return [t for t in self.teams.values() if t["event_id"] == event_id]

    def is_member(self, team_id, user_id):
        return (team_id, user_id) in self.members

    def add_member(self, **kwargs):
        self.members.add((kwargs["team_id"], kwargs["user_id"]))
        return {
            "team_id": kwargs["team_id"],
            "user_id": kwargs["user_id"],
            "membership_role": kwargs["membership_role"],
            "created_at": None,
        }

    def remove_member(self, **kwargs):
        key = (kwargs["team_id"], kwargs["user_id"])
        if key in self.members:
            self.members.remove(key)
            return True
        return False

    def list_members(self, team_id):
        return []


def test_admin_can_create_team():
    repository = FakeRepository()
    service = TeamService(repository)
    event_id = uuid4()

    team = service.create(event_id=event_id, name="Red")

    assert team["name"] == "Red"


def test_duplicate_team_name_is_rejected():
    repository = FakeRepository()
    service = TeamService(repository)
    event_id = uuid4()

    service.create(event_id=event_id, name="Red")

    with pytest.raises(HTTPException) as exc:
        service.create(event_id=event_id, name="Red")

    assert exc.value.status_code == 409


def test_lead_can_manage_team_members_when_on_team():
    repository = FakeRepository()
    service = TeamService(repository)
    team = repository.create(event_id=uuid4(), name="Red")
    lead_id = uuid4()

    repository.members.add((team["id"], lead_id))

    result = service.add_member(
        team_id=team["id"],
        user_id=uuid4(),
        membership_role="MEMBER",
        actor_id=lead_id,
        actor_role="LEAD",
    )

    assert result["membership_role"] == "MEMBER"


def test_member_cannot_manage_team_members():
    repository = FakeRepository()
    service = TeamService(repository)
    team = repository.create(event_id=uuid4(), name="Red")

    with pytest.raises(HTTPException) as exc:
        service.add_member(
            team_id=team["id"],
            user_id=uuid4(),
            membership_role="MEMBER",
            actor_id=uuid4(),
            actor_role="MEMBER",
        )

    assert exc.value.status_code == 403
