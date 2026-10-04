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

    def list_all(self):
        return self.repository.list_all()

    def get(self, event_id: UUID):
        event = self.repository.get(event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")
        return event

    def transition(self, event_id: UUID, target_state: str):
        event = self.get(event_id)
        current_state = str(event["state"])

        if target_state not in ALLOWED_TRANSITIONS.get(current_state, set()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event transition: {current_state} -> {target_state}",
            )

        return self.repository.update_state(event_id, target_state)
