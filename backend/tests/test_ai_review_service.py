from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.ai.reviewer import (
    AiReviewProviderError,
    AiReviewResult,
    SubmissionReviewInput,
)
from app.services.ai_review_service import AiReviewService


class FakeRepository:
    def __init__(self):
        self.submission_id = uuid4()
        self.task_id = uuid4()
        self.team_id = uuid4()
        self.saved = []
        self.recent_count = 0

    def get(self, submission_id):
        if submission_id != self.submission_id:
            return None
        return {
            "id": self.submission_id,
            "task_id": self.task_id,
            "submitted_by": uuid4(),
            "content": "Implemented the requested API and added tests.",
        }

    def get_task_for_ai(self, task_id):
        if task_id != self.task_id:
            return None
        return {
            "id": self.task_id,
            "team_id": self.team_id,
            "title": "Implement API",
            "description": "Build the API endpoint and include tests.",
            "state": "SUBMITTED",
        }

    def is_team_member(self, team_id, user_id):
        return True

    def count_recent_ai_evaluations(self, submission_id, requested_by, cooldown_seconds):
        return self.recent_count

    def create_ai_evaluation(self, **kwargs):
        self.saved.append(kwargs)
        return {
            "id": uuid4(),
            **kwargs,
            "created_at": "2026-10-05T00:00:00Z",
        }

    def list_ai_evaluations(self, submission_id):
        return self.saved

    def commit(self):
        pass

    def rollback(self):
        pass


class FakeAudit:
    def __init__(self):
        self.records = []

    def record(self, **kwargs):
        self.records.append(kwargs)


class FakeReviewer:
    def __init__(self):
        self.received = None

    def review(self, payload: SubmissionReviewInput):
        self.received = payload
        return AiReviewResult(
            score=90,
            recommendation="APPROVE",
            summary="The submission addresses the task.",
            strengths=["Includes tests"],
            issues=[],
        )


class FailingReviewer:
    def review(self, payload: SubmissionReviewInput):
        raise AiReviewProviderError("provider failed")


def build_service(repository, reviewer):
    return AiReviewService(
        repository,
        reviewer,
        "gemini-3.8-flash",
        FakeAudit(),
        cooldown_seconds=10,
    )


def test_ai_review_uses_submission_and_task_context_and_persists_result():
    repository = FakeRepository()
    reviewer = FakeReviewer()
    audit = FakeAudit()
    service = AiReviewService(
        repository,
        reviewer,
        "gemini-3.8-flash",
        audit,
        cooldown_seconds=10,
    )

    result = service.review_submission(repository.submission_id, uuid4(), "LEAD")

    assert result["recommendation"] == "APPROVE"
    assert result["score"] == 90
    assert result["model"] == "gemini-3.8-flash"
    assert len(repository.saved) == 1
    assert reviewer.received.task_title == "Implement API"
    assert "API" in reviewer.received.submission_content
    assert audit.records[0]["action"] == "AI_REVIEW_REQUESTED"
    assert audit.records[0]["metadata"]["recommendation"] == "APPROVE"


def test_persisted_evaluations_are_available_to_reviewers():
    repository = FakeRepository()
    reviewer = FakeReviewer()
    service = build_service(repository, reviewer)
    actor_id = uuid4()

    service.review_submission(repository.submission_id, actor_id, "LEAD")
    evaluations = service.list_evaluations(repository.submission_id, actor_id, "LEAD")

    assert len(evaluations) == 1


def test_members_cannot_request_ai_review():
    repository = FakeRepository()
    service = build_service(repository, FakeReviewer())

    with pytest.raises(HTTPException) as exc:
        service.review_submission(repository.submission_id, uuid4(), "MEMBER")

    assert exc.value.status_code == 403


def test_ai_review_is_rate_limited_by_persisted_history():
    repository = FakeRepository()
    repository.recent_count = 1
    service = build_service(repository, FakeReviewer())

    with pytest.raises(HTTPException) as exc:
        service.review_submission(repository.submission_id, uuid4(), "LEAD")

    assert exc.value.status_code == 429


def test_ai_provider_failure_does_not_create_evaluation():
    repository = FakeRepository()
    service = build_service(repository, FailingReviewer())

    with pytest.raises(HTTPException) as exc:
        service.review_submission(repository.submission_id, uuid4(), "LEAD")

    assert exc.value.status_code == 503
    assert repository.saved == []


def test_review_input_rejects_oversized_submission():
    with pytest.raises(ValueError):
        SubmissionReviewInput(
            task_title="Implement API",
            task_description=None,
            submission_content="x" * 12001,
        )


def test_ai_result_rejects_invalid_recommendation():
    with pytest.raises(ValueError):
        AiReviewResult(
            score=80,
            recommendation="MAYBE",
            summary="Insufficient evidence.",
            strengths=[],
            issues=[],
        )
