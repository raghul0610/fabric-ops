from uuid import UUID

from fastapi import HTTPException, status

from app.repositories.audit_repository import AuditRepository
from app.repositories.submission_repository import SubmissionRepository


class SubmissionService:
    def __init__(self, repository: SubmissionRepository, audit: AuditRepository) -> None:
        self.repository = repository
        self.audit = audit

    def create(self, task_id: UUID, actor_id: UUID, content: str):
        task = self.repository.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if task["assignee_id"] != actor_id:
            raise HTTPException(status_code=403, detail="Only the assignee can submit this task")
        if str(task["state"]) != "IN_PROGRESS":
            raise HTTPException(status_code=400, detail="Only in-progress tasks can be submitted")

        try:
            submission = self.repository.create(task_id, actor_id, content)
            self.repository.set_task_state(task_id, "SUBMITTED")
            self.audit.record(
                actor_id=actor_id,
                action="SUBMISSION_CREATED",
                entity_type="submission",
                entity_id=submission["id"],
                metadata={"task_id": str(task_id)},
            )
            self.repository.commit()
            return submission
        except Exception:
            self.repository.rollback()
            raise

    def get(self, submission_id: UUID, actor_id: UUID, actor_role: str):
        submission = self.repository.get(submission_id)
        if submission is None:
            raise HTTPException(status_code=404, detail="Submission not found")

        task = self.repository.get_task(submission["task_id"])
        if actor_role != "ADMIN" and actor_role != "LEAD" and submission["submitted_by"] != actor_id:
            raise HTTPException(status_code=403, detail="Insufficient submission permissions")
        if actor_role == "LEAD" and not self.repository.is_team_member(task["team_id"], actor_id):
            raise HTTPException(status_code=403, detail="Insufficient submission permissions")
        return submission

    def list_for_task(self, task_id: UUID, actor_id: UUID, actor_role: str):
        task = self.repository.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if actor_role == "LEAD" and not self.repository.is_team_member(task["team_id"], actor_id):
            raise HTTPException(status_code=403, detail="Insufficient submission permissions")
        if actor_role == "MEMBER" and task["assignee_id"] != actor_id:
            raise HTTPException(status_code=403, detail="Insufficient submission permissions")
        return self.repository.list_for_task(task_id)

    def review(
        self,
        submission_id: UUID,
        actor_id: UUID,
        actor_role: str,
        decision: str,
        feedback: str | None,
    ):
        if actor_role not in {"ADMIN", "LEAD"}:
            raise HTTPException(status_code=403, detail="Only reviewers can review submissions")

        submission = self.repository.get(submission_id)
        if submission is None:
            raise HTTPException(status_code=404, detail="Submission not found")

        task = self.repository.get_task(submission["task_id"])
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        if submission["submitted_by"] == actor_id:
            raise HTTPException(status_code=403, detail="Reviewer cannot be the submitter")

        if actor_role == "LEAD" and not self.repository.is_team_member(task["team_id"], actor_id):
            raise HTTPException(status_code=403, detail="Lead is not a member of this task's team")

        if str(task["state"]) != "SUBMITTED":
            raise HTTPException(status_code=400, detail="Only submitted tasks can be reviewed")

        try:
            review = self.repository.create_review(
                submission_id,
                actor_id,
                decision,
                feedback,
            )
            self.repository.set_task_state(
                task["id"],
                "APPROVED" if decision == "APPROVED" else "REJECTED",
            )
            self.audit.record(
                actor_id=actor_id,
                action=f"SUBMISSION_{decision}",
                entity_type="submission",
                entity_id=submission_id,
                metadata={"task_id": str(task["id"]), "review_id": str(review["id"])},
            )
            self.repository.commit()
            return review
        except Exception:
            self.repository.rollback()
            raise
