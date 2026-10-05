from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


class EventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        name: str,
        description: str | None,
        starts_at,
        ends_at,
    ):
        row = self.db.execute(
            text("""
                INSERT INTO public.events (name, description, starts_at, ends_at)
                VALUES (:name, :description, :starts_at, :ends_at)
                RETURNING id, name, description, state, starts_at, ends_at, created_at, updated_at
            """),
            {
                "name": name,
                "description": description,
                "starts_at": starts_at,
                "ends_at": ends_at,
            },
        ).mappings().one()
        self.db.commit()
        return row

    def list_all(self):
        return self.db.execute(
            text("""
                SELECT id, name, description, state, starts_at, ends_at, created_at, updated_at
                FROM public.events
                ORDER BY starts_at ASC
            """)
        ).mappings().all()

    def list_for_user(self, user_id: UUID):
        return self.db.execute(
            text("""
                SELECT DISTINCT e.id, e.name, e.description, e.state,
                                e.starts_at, e.ends_at, e.created_at, e.updated_at
                FROM public.events e
                JOIN public.teams t ON t.event_id = e.id
                JOIN public.team_members tm ON tm.team_id = t.id
                WHERE tm.user_id = :user_id
                ORDER BY e.starts_at ASC
            """),
            {"user_id": str(user_id)},
        ).mappings().all()

    def get(self, event_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, name, description, state, starts_at, ends_at, created_at, updated_at
                FROM public.events
                WHERE id = :event_id
            """),
            {"event_id": str(event_id)},
        ).mappings().first()

    def is_team_member_of_event(self, event_id: UUID, user_id: UUID) -> bool:
        return self.db.execute(
            text("""
                SELECT 1
                FROM public.teams t
                JOIN public.team_members tm ON tm.team_id = t.id
                WHERE t.event_id = :event_id
                  AND tm.user_id = :user_id
                LIMIT 1
            """),
            {"event_id": str(event_id), "user_id": str(user_id)},
        ).first() is not None

    def update_state(self, event_id: UUID, state: str):
        row = self.db.execute(
            text("""
                UPDATE public.events
                SET state = :state
                WHERE id = :event_id
                RETURNING id, name, description, state, starts_at, ends_at, created_at, updated_at
            """),
            {"event_id": str(event_id), "state": state},
        ).mappings().first()
        self.db.commit()
        return row
