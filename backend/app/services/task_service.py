from uuid import UUID

from fastapi import HTTPException, status

from app.repositories.task_repository import TaskRepository


ALLOWED_TRANSITIONS = {
    "TODO": {"IN_PROGRESS"},
    "IN_PROGRESS": {"SUBMITTED"},
    "SUBMITTED": {"APPROVED", "REJECTED"},
    "APPROVED": set(),
    "REJECTED": {"IN_PROGRESS"},
}


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def create(
        self,
        *,
        event_id: UUID,
        team_id: UUID,
        title: str,
        description: str | None,
        assignee_id: UUID,
        actor_id: UUID,
        actor_role: str,
    ):
        if not self.repository.team_exists_in_event(team_id, event_id):
            raise HTTPException(
                status_code=404,
                detail="Team not found for event",
            )

        if not self.repository.is_team_member(team_id, assignee_id):
            raise HTTPException(
                status_code=400,
                detail="Assignee must be a member of the team",
            )

        if actor_role != "ADMIN" and not self.repository.is_team_member(team_id, actor_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient team permissions",
            )

        return self.repository.create(
            event_id=event_id,
            team_id=team_id,
            title=title,
            description=description,
            assignee_id=assignee_id,
        )

    def get(self, task_id: UUID):
        task = self.repository.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def list_for_team(self, team_id: UUID, *, actor_id: UUID, actor_role: str):
        if actor_role != "ADMIN" and not self.repository.is_team_member(team_id, actor_id):
            raise HTTPException(status_code=403, detail="Insufficient team permissions")
        return self.repository.list_for_team(team_id)

    def list_for_assignee(self, assignee_id: UUID, *, actor_id: UUID):
        if assignee_id != actor_id:
            raise HTTPException(status_code=403, detail="Cannot view another member's tasks")
        return self.repository.list_for_assignee(assignee_id)

    def transition(
        self,
        task_id: UUID,
        target_state: str,
        *,
        actor_id: UUID,
        actor_role: str,
    ):
        task = self.get(task_id)
        current_state = str(task["state"])

        if actor_role == "ADMIN":
            allowed = True
        elif actor_role == "LEAD":
            allowed = self.repository.is_team_member(task["team_id"], actor_id)
        else:
            allowed = task["assignee_id"] == actor_id

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient task permissions",
            )

        if target_state not in ALLOWED_TRANSITIONS.get(current_state, set()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid task transition: {current_state} -> {target_state}",
            )

        if actor_role == "MEMBER" and target_state not in {"IN_PROGRESS", "SUBMITTED"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members may only work on or submit assigned tasks",
            )

        if actor_role == "LEAD" and target_state not in {"APPROVED", "REJECTED"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Leads may only approve or reject submitted tasks",
            )

        if target_state in {"APPROVED", "REJECTED"} and current_state != "SUBMITTED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only submitted tasks can be reviewed",
            )

        return self.repository.update_state(task_id, target_state)
