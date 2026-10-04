from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services.submission_service import SubmissionService


class FakeRepository:
    def __init__(self, state="IN_PROGRESS"):
        self.task = {
            "id": uuid4(),
            "event_id": uuid4(),
            "team_id": uuid4(),
            "assignee_id": uuid4(),
            "state": state,
        }
        self.submission = None
        self.review = None

    def get_task(self, task_id):
        return self.task if task_id == self.task["id"] else None

    def create(self, task_id, submitted_by, content):
        self.submission = {
            "id": uuid4(),
            "task_id": task_id,
            "submitted_by": submitted_by,
            "content": content,
        }
        return self.submission

    def get(self, submission_id):
        return self.submission if self.submission and self.submission["id"] == submission_id else None

    def list_for_task(self, task_id):
        return [self.submission] if self.submission else []

    def is_team_member(self, team_id, user_id):
        return user_id == self.task["assignee_id"] and team_id == self.task["team_id"]

    def set_task_state(self, task_id, state):
        self.task["state"] = state

    def create_review(self, submission_id, reviewer_id, decision, feedback):
        self.review = {
            "id": uuid4(),
            "submission_id": submission_id,
            "reviewer_id": reviewer_id,
            "decision": decision,
            "feedback": feedback,
        }
        return self.review


class FakeAudit:
    def __init__(self):
        self.records = []

    def record(self, **kwargs):
        self.records.append(kwargs)


def test_member_can_create_submission_for_in_progress_task():
    repository = FakeRepository()
    audit = FakeAudit()
    service = SubmissionService(repository, audit)

    result = service.create(
        repository.task["id"],
        repository.task["assignee_id"],
        "https://example.com/submission",
    )

    assert result["submitted_by"] == repository.task["assignee_id"]
    assert repository.task["state"] == "SUBMITTED"
    assert audit.records[0]["action"] == "SUBMISSION_CREATED"


def test_non_assignee_cannot_submit():
    repository = FakeRepository()
    service = SubmissionService(repository, FakeAudit())

    with pytest.raises(HTTPException) as exc:
        service.create(repository.task["id"], uuid4(), "work")

    assert exc.value.status_code == 403


def test_reviewer_cannot_be_submitter():
    repository = FakeRepository("SUBMITTED")
    submitter = repository.task["assignee_id"]
    repository.submission = {
        "id": uuid4(),
        "task_id": repository.task["id"],
        "submitted_by": submitter,
        "content": "work",
    }
    service = SubmissionService(repository, FakeAudit())

    with pytest.raises(HTTPException) as exc:
        service.review(
            repository.submission["id"],
            submitter,
            "ADMIN",
            "APPROVED",
            None,
        )

    assert exc.value.status_code == 403


def test_admin_can_review_submission():
    repository = FakeRepository("SUBMITTED")
    repository.submission = {
        "id": uuid4(),
        "task_id": repository.task["id"],
        "submitted_by": repository.task["assignee_id"],
        "content": "work",
    }
    service = SubmissionService(repository, FakeAudit())

    result = service.review(
        repository.submission["id"],
        uuid4(),
        "ADMIN",
        "APPROVED",
        "Looks good",
    )

    assert result["decision"] == "APPROVED"
    assert repository.task["state"] == "APPROVED"
    assert service.audit.records[0]["action"] == "SUBMISSION_APPROVED"
