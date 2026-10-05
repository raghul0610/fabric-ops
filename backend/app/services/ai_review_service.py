from uuid import UUID

from fastapi import HTTPException, status

from app.ai.reviewer import AiReviewResult, SubmissionReviewInput, SubmissionReviewer
from app.repositories.submission_repository import SubmissionRepository


class AiReviewService:
    def __init__(
        self,
        repository: SubmissionRepository,
        reviewer: SubmissionReviewer,
    ) -> None:
        self.repository = repository
        self.reviewer = reviewer

    def review_submission(
        self,
        submission_id: UUID,
        actor_id: UUID,
        actor_role: str,
    ) -> AiReviewResult:
        if actor_role not in {"ADMIN", "LEAD"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only reviewers can request AI reviews",
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

        if str(task["state"]) != "SUBMITTED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only submitted tasks can be evaluated",
            )

        return self.reviewer.review(
            SubmissionReviewInput(
                task_title=task["title"],
                task_description=task["description"],
                submission_content=submission["content"],
            )
        )
