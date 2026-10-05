from uuid import UUID

from fastapi import HTTPException, status

from app.repositories.event_repository import EventRepository


ALLOWED_TRANSITIONS = {
    "DRAFT": {"PLANNED"},
    "PLANNED": {"ACTIVE", "CANCELLED"},
    "ACTIVE": {"COMPLETED", "CANCELLED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}


class EventService:
    def __init__(self, repository: EventRepository) -> None:
        self.repository = repository

    def create(self, *, name, description, starts_at, ends_at):
        if ends_at <= starts_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event end time must be after start time",
            )
        return self.repository.create(
            name=name,
            description=description,
            starts_at=starts_at,
            ends_at=ends_at,
        )

    def list_all(self, *, actor_id: UUID, actor_role: str):
        if actor_role == "ADMIN":
            return self.repository.list_all()
        return self.repository.list_for_user(actor_id)

    def get(self, event_id: UUID, *, actor_id: UUID, actor_role: str):
        event = self.repository.get(event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")

        if actor_role != "ADMIN" and not self.repository.is_team_member_of_event(event_id, actor_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient event permissions",
            )

        return event

    def transition(
        self,
        event_id: UUID,
        target_state: str,
        *,
        actor_id: UUID,
        actor_role: str,
    ):
        event = self.get(event_id, actor_id=actor_id, actor_role=actor_role)

        if actor_role not in {"ADMIN", "LEAD"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators and leads can change event state",
            )

        current_state = str(event["state"])

        if target_state not in ALLOWED_TRANSITIONS.get(current_state, set()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event transition: {current_state} -> {target_state}",
            )

        return self.repository.update_state(event_id, target_state)
