from uuid import UUID

from fastapi import HTTPException, status

from app.ai.reviewer import (
    AiReviewProviderError,
    SubmissionReviewInput,
    SubmissionReviewer,
)
from app.repositories.audit_repository import AuditRepository
from app.repositories.submission_repository import SubmissionRepository


class AiReviewService:
    def __init__(
        self,
        repository: SubmissionRepository,
        reviewer: SubmissionReviewer | None,
        model: str,
        audit: AuditRepository,
        cooldown_seconds: int = 10,
    ) -> None:
        self.repository = repository
        self.reviewer = reviewer
        self.model = model
        self.audit = audit
        self.cooldown_seconds = cooldown_seconds

    def _authorize(self, submission_id: UUID, actor_id: UUID, actor_role: str):
        if actor_role not in {"ADMIN", "LEAD"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only reviewers can access AI evaluations",
            )

        submission = self.repository.get(submission_id)
        if submission is None:
            raise HTTPException(status_code=404, detail="Submission not found")

        task = self.repository.get_task_for_ai(submission["task_id"])
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        if actor_role == "LEAD" and not self.repository.is_team_member(task["team_id"], actor_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Lead is not a member of this task's team",
            )

        return submission, task

    def review_submission(
        self,
        submission_id: UUID,
        actor_id: UUID,
        actor_role: str,
    ):
        submission, task = self._authorize(submission_id, actor_id, actor_role)

        if self.reviewer is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI review is not configured",
            )

        if str(task["state"]) != "SUBMITTED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only submitted tasks can be evaluated",
            )

        if self.cooldown_seconds > 0:
            recent_count = self.repository.count_recent_ai_evaluations(
                submission_id,
                actor_id,
                self.cooldown_seconds,
            )
            if recent_count:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Please wait {self.cooldown_seconds} seconds before requesting another AI evaluation",
                )

        try:
            payload = SubmissionReviewInput(
                task_title=task["title"],
                task_description=task["description"],
                submission_content=submission["content"],
            )
            result = self.reviewer.review(payload)
        except AiReviewProviderError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI review provider is temporarily unavailable",
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submission is not valid for AI evaluation",
            ) from exc

        try:
            evaluation = self.repository.create_ai_evaluation(
                submission_id=submission_id,
                requested_by=actor_id,
                model=self.model,
                score=result.score,
                recommendation=result.recommendation,
                summary=result.summary,
                strengths=result.strengths,
                issues=result.issues,
            )
            self.audit.record(
                actor_id=actor_id,
                action="AI_REVIEW_REQUESTED",
                entity_type="submission",
                entity_id=submission_id,
                metadata={
                    "evaluation_id": str(evaluation["id"]),
                    "model": self.model,
                    "score": result.score,
                    "recommendation": result.recommendation,
                },
            )
            self.repository.commit()
            return evaluation
        except Exception:
            self.repository.rollback()
            raise

    def list_evaluations(
        self,
        submission_id: UUID,
        actor_id: UUID,
        actor_role: str,
    ):
        self._authorize(submission_id, actor_id, actor_role)
        return self.repository.list_ai_evaluations(submission_id)
