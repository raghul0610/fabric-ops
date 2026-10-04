from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth import CurrentUser, require_role
from app.db import get_db
from app.repositories.team_repository import TeamRepository
from app.schemas.team import (
    TeamCreate,
    TeamMemberAdd,
    TeamMemberResponse,
    TeamResponse,
)
from app.services.team_service import TeamService


router = APIRouter(tags=["teams"])


def get_team_service(db=Depends(get_db)) -> TeamService:
    return TeamService(TeamRepository(db))


@router.post(
    "/events/{event_id}/teams",
    response_model=TeamResponse,
    status_code=201,
)
def create_team(
    event_id: UUID,
    payload: TeamCreate,
    _: CurrentUser = Depends(require_role("ADMIN")),
    service: TeamService = Depends(get_team_service),
):
    return service.create(event_id=event_id, name=payload.name)


@router.get(
    "/events/{event_id}/teams",
    response_model=list[TeamResponse],
)
def list_event_teams(
    event_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: TeamService = Depends(get_team_service),
):
    return service.list_for_event(
        event_id,
        user_id=user.id,
        is_admin=user.role == "ADMIN",
    )


@router.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: TeamService = Depends(get_team_service),
):
    team = service.get(team_id)
    if user.role != "ADMIN" and not service.repository.is_member(team_id, user.id):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Insufficient team permissions")
    return team


@router.get(
    "/teams/{team_id}/members",
    response_model=list[TeamMemberResponse],
)
def list_team_members(
    team_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: TeamService = Depends(get_team_service),
):
    return service.list_members(team_id, actor_id=user.id, actor_role=user.role)


@router.post(
    "/teams/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=201,
)
def add_team_member(
    team_id: UUID,
    payload: TeamMemberAdd,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD")),
    service: TeamService = Depends(get_team_service),
):
    return service.add_member(
        team_id=team_id,
        user_id=payload.user_id,
        membership_role=payload.membership_role,
        actor_id=user.id,
        actor_role=user.role,
    )


@router.delete("/teams/{team_id}/members/{user_id}", status_code=204)
def remove_team_member(
    team_id: UUID,
    user_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD")),
    service: TeamService = Depends(get_team_service),
):
    service.remove_member(
        team_id=team_id,
        user_id=user_id,
        actor_id=user.id,
        actor_role=user.role,
    )
