from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth import CurrentUser, require_role
from app.db import get_db
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate, EventResponse, EventStateUpdate
from app.services.event_service import EventService


router = APIRouter(prefix="/events", tags=["events"])


def get_event_service(db=Depends(get_db)) -> EventService:
    return EventService(EventRepository(db))


@router.get("/me")
def events_for_current_user(
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
) -> dict[str, str]:
    return {"user_id": str(user.id), "role": user.role}


@router.post("", response_model=EventResponse, status_code=201)
def create_event(
    payload: EventCreate,
    _: CurrentUser = Depends(require_role("ADMIN")),
    service: EventService = Depends(get_event_service),
):
    return service.create(**payload.model_dump())


@router.get("", response_model=list[EventResponse])
def list_events(
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: EventService = Depends(get_event_service),
):
    return service.list_all(actor_id=user.id, actor_role=user.role)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: EventService = Depends(get_event_service),
):
    return service.get(event_id, actor_id=user.id, actor_role=user.role)


@router.patch("/{event_id}/state", response_model=EventResponse)
def update_event_state(
    event_id: UUID,
    payload: EventStateUpdate,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD")),
    service: EventService = Depends(get_event_service),
):
    return service.transition(
        event_id,
        payload.state,
        actor_id=user.id,
        actor_role=user.role,
    )
