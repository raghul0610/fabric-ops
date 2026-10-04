from uuid import UUID

from fastapi import HTTPException, status

from app.repositories.team_repository import TeamRepository


class TeamService:
    def __init__(self, repository: TeamRepository) -> None:
        self.repository = repository

    def create(self, *, event_id: UUID, name: str):
        if not self.repository.event_exists(event_id):
            raise HTTPException(status_code=404, detail="Event not found")

        if self.repository.team_name_exists(event_id, name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Team name already exists for this event",
            )

        return self.repository.create(event_id=event_id, name=name)

    def get(self, team_id: UUID):
        team = self.repository.get(team_id)
        if team is None:
            raise HTTPException(status_code=404, detail="Team not found")
        return team

    def list_for_event(self, event_id: UUID, *, user_id: UUID, is_admin: bool):
        if not self.repository.event_exists(event_id):
            raise HTTPException(status_code=404, detail="Event not found")
        return self.repository.list_for_event(
            event_id, user_id=user_id, is_admin=is_admin
        )

    def can_manage_members(self, team_id: UUID, user_id: UUID, role: str) -> bool:
        return role == "ADMIN" or (
            role == "LEAD" and self.repository.is_member(team_id, user_id)
        )

    def add_member(
        self,
        *,
        team_id: UUID,
        user_id: UUID,
        membership_role: str,
        actor_id: UUID,
        actor_role: str,
    ):
        self.get(team_id)

        if not self.can_manage_members(team_id, actor_id, actor_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient team permissions",
            )

        try:
            return self.repository.add_member(
                team_id=team_id,
                user_id=user_id,
                membership_role=membership_role,
            )
        except Exception as exc:
            self.repository.db.rollback()
            message = str(exc)
            if "team_members_pkey" in message or "duplicate key" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User is already a team member",
                ) from exc
            if "team_members_user_id_fkey" in message:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Application user not found",
                ) from exc
            raise

    def remove_member(
        self,
        *,
        team_id: UUID,
        user_id: UUID,
        actor_id: UUID,
        actor_role: str,
    ):
        self.get(team_id)

        if not self.can_manage_members(team_id, actor_id, actor_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient team permissions",
            )

        if not self.repository.remove_member(team_id=team_id, user_id=user_id):
            raise HTTPException(status_code=404, detail="Team member not found")

    def list_members(self, team_id: UUID, *, actor_id: UUID, actor_role: str):
        self.get(team_id)
        if actor_role != "ADMIN" and not self.repository.is_member(team_id, actor_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient team permissions",
            )
        return self.repository.list_members(team_id)
