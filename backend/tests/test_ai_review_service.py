from uuid import uuid4

from app.ai.reviewer import AiReviewResult, SubmissionReviewInput
from app.services.ai_review_service import AiReviewService


class FakeRepository:
    def __init__(self):
        self.submission_id = uuid4()
        self.task_id = uuid4()
        self.team_id = uuid4()

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


def test_ai_review_uses_submission_and_task_context():
    repository = FakeRepository()
    reviewer = FakeReviewer()
    service = AiReviewService(repository, reviewer)

    result = service.review_submission(repository.submission_id, uuid4(), "LEAD")

    assert result.recommendation == "APPROVE"
    assert reviewer.received.task_title == "Implement API"
    assert "API" in reviewer.received.submission_content


def test_members_cannot_request_ai_review():
    repository = FakeRepository()
    reviewer = FakeReviewer()
    service = AiReviewService(repository, reviewer)

    try:
        service.review_submission(repository.submission_id, uuid4(), "MEMBER")
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 403
    else:
        raise AssertionError("Expected a 403 response")
