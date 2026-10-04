from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth import CurrentUser, require_role
from app.db import get_db
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskStateUpdate
from app.services.task_service import TaskService


router = APIRouter(tags=["tasks"])


def get_task_service(db=Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db))


@router.post(
    "/events/{event_id}/teams/{team_id}/tasks",
    response_model=TaskResponse,
    status_code=201,
)
def create_task(
    event_id: UUID,
    team_id: UUID,
    payload: TaskCreate,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD")),
    service: TaskService = Depends(get_task_service),
):
    return service.create(
        event_id=event_id,
        team_id=team_id,
        title=payload.title,
        description=payload.description,
        assignee_id=payload.assignee_id,
        actor_id=user.id,
        actor_role=user.role,
    )


@router.get(
    "/teams/{team_id}/tasks",
    response_model=list[TaskResponse],
)
def list_team_tasks(
    team_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: TaskService = Depends(get_task_service),
):
    return service.list_for_team(team_id, actor_id=user.id, actor_role=user.role)


@router.get(
    "/tasks/me",
    response_model=list[TaskResponse],
)
def list_my_tasks(
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: TaskService = Depends(get_task_service),
):
    return service.list_for_assignee(user.id, actor_id=user.id)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: TaskService = Depends(get_task_service),
):
    task = service.get(task_id)
    if user.role == "ADMIN":
        return task
    if user.role == "LEAD" and service.repository.is_team_member(task["team_id"], user.id):
        return task
    if task["assignee_id"] == user.id:
        return task

    from fastapi import HTTPException
    raise HTTPException(status_code=403, detail="Insufficient task permissions")


@router.patch(
    "/tasks/{task_id}/state",
    response_model=TaskResponse,
)
def update_task_state(
    task_id: UUID,
    payload: TaskStateUpdate,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: TaskService = Depends(get_task_service),
):
    return service.transition(
        task_id,
        payload.state,
        actor_id=user.id,
        actor_role=user.role,
    )
