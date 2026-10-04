from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services.task_service import TaskService


class FakeRepository:
    def __init__(self, state="TODO"):
        self.task = {
            "id": uuid4(),
            "event_id": uuid4(),
            "team_id": uuid4(),
            "title": "Task",
            "description": None,
            "assignee_id": uuid4(),
            "state": state,
        }
        self.members = {self.task["assignee_id"]}

    def team_exists_in_event(self, team_id, event_id):
        return team_id == self.task["team_id"] and event_id == self.task["event_id"]

    def is_team_member(self, team_id, user_id):
        return user_id in self.members and team_id == self.task["team_id"]

    def create(self, **kwargs):
        return {**self.task, **kwargs, "id": uuid4()}

    def get(self, task_id):
        return self.task if task_id == self.task["id"] else None

    def list_for_team(self, team_id):
        return [self.task]

    def list_for_assignee(self, assignee_id):
        return [self.task]

    def update_state(self, task_id, state):
        self.task["state"] = state
        return self.task


def test_member_can_start_task():
    repository = FakeRepository("TODO")
    service = TaskService(repository)
    service.transition(
        repository.task["id"],
        "IN_PROGRESS",
        actor_id=repository.task["assignee_id"],
        actor_role="MEMBER",
    )
    assert repository.task["state"] == "IN_PROGRESS"


def test_member_cannot_submit_directly():
    repository = FakeRepository("IN_PROGRESS")
    service = TaskService(repository)

    with pytest.raises(HTTPException) as exc:
        service.transition(
            repository.task["id"],
            "SUBMITTED",
            actor_id=repository.task["assignee_id"],
            actor_role="MEMBER",
        )

    assert exc.value.status_code == 403


def test_review_states_require_submission_review_endpoint():
    repository = FakeRepository("SUBMITTED")
    service = TaskService(repository)

    with pytest.raises(HTTPException) as exc:
        service.transition(
            repository.task["id"],
            "APPROVED",
            actor_id=uuid4(),
            actor_role="ADMIN",
        )

    assert exc.value.status_code == 400
    assert repository.task["state"] == "SUBMITTED"


def test_lead_cannot_change_review_state_directly():
    repository = FakeRepository("SUBMITTED")
    lead = uuid4()
    repository.members.add(lead)
    service = TaskService(repository)

    with pytest.raises(HTTPException) as exc:
        service.transition(
            repository.task["id"],
            "REJECTED",
            actor_id=lead,
            actor_role="LEAD",
        )

    assert exc.value.status_code == 400
    assert repository.task["state"] == "SUBMITTED"


def test_rejected_task_can_return_to_in_progress():
    repository = FakeRepository("REJECTED")
    service = TaskService(repository)

    result = service.transition(
        repository.task["id"],
        "IN_PROGRESS",
        actor_id=repository.task["assignee_id"],
        actor_role="MEMBER",
    )
    assert result["state"] == "IN_PROGRESS"


def test_invalid_transition_is_rejected():
    repository = FakeRepository("TODO")
    service = TaskService(repository)

    with pytest.raises(HTTPException) as exc:
        service.transition(
            repository.task["id"],
            "SUBMITTED",
            actor_id=repository.task["assignee_id"],
            actor_role="MEMBER",
        )

    assert exc.value.status_code == 400 or exc.value.status_code == 403


def test_assignee_must_belong_to_team():
    repository = FakeRepository()
    service = TaskService(repository)

    with pytest.raises(HTTPException) as exc:
        service.create(
            event_id=repository.task["event_id"],
            team_id=repository.task["team_id"],
            title="Task",
            description=None,
            assignee_id=uuid4(),
            actor_id=repository.task["assignee_id"],
            actor_role="MEMBER",
        )

    assert exc.value.status_code == 400
