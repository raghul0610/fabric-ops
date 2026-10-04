from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


class TeamRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def event_exists(self, event_id: UUID) -> bool:
        return self.db.execute(
            text("SELECT 1 FROM public.events WHERE id = :event_id"),
            {"event_id": str(event_id)},
        ).first() is not None

    def team_name_exists(self, event_id: UUID, name: str) -> bool:
        return self.db.execute(
            text("""
                SELECT 1
                FROM public.teams
                WHERE event_id = :event_id AND name = :name
            """),
            {"event_id": str(event_id), "name": name},
        ).first() is not None

    def create(self, *, event_id: UUID, name: str):
        row = self.db.execute(
            text("""
                INSERT INTO public.teams (event_id, name)
                VALUES (:event_id, :name)
                RETURNING id, event_id, name, created_at
            """),
            {"event_id": str(event_id), "name": name},
        ).mappings().one()
        self.db.commit()
        return row

    def get(self, team_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, event_id, name, created_at
                FROM public.teams
                WHERE id = :team_id
            """),
            {"team_id": str(team_id)},
        ).mappings().first()

    def list_for_event(self, event_id: UUID, *, user_id: UUID, is_admin: bool):
        if is_admin:
            query = """
                SELECT id, event_id, name, created_at
                FROM public.teams
                WHERE event_id = :event_id
                ORDER BY created_at ASC
            """
            params = {"event_id": str(event_id)}
        else:
            query = """
                SELECT t.id, t.event_id, t.name, t.created_at
                FROM public.teams t
                JOIN public.team_members tm ON tm.team_id = t.id
                WHERE t.event_id = :event_id AND tm.user_id = :user_id
                ORDER BY t.created_at ASC
            """
            params = {"event_id": str(event_id), "user_id": str(user_id)}

        return self.db.execute(text(query), params).mappings().all()

    def is_member(self, team_id: UUID, user_id: UUID) -> bool:
        return self.db.execute(
            text("""
                SELECT 1
                FROM public.team_members
                WHERE team_id = :team_id AND user_id = :user_id
            """),
            {"team_id": str(team_id), "user_id": str(user_id)},
        ).first() is not None

    def add_member(self, *, team_id: UUID, user_id: UUID, membership_role: str):
        row = self.db.execute(
            text("""
                INSERT INTO public.team_members (team_id, user_id, membership_role)
                VALUES (:team_id, :user_id, :membership_role)
                RETURNING team_id, user_id, membership_role, created_at
            """),
            {
                "team_id": str(team_id),
                "user_id": str(user_id),
                "membership_role": membership_role,
            },
        ).mappings().one()
        self.db.commit()
        return row

    def remove_member(self, *, team_id: UUID, user_id: UUID) -> bool:
        result = self.db.execute(
            text("""
                DELETE FROM public.team_members
                WHERE team_id = :team_id AND user_id = :user_id
            """),
            {"team_id": str(team_id), "user_id": str(user_id)},
        )
        self.db.commit()
        return result.rowcount > 0

    def list_members(self, team_id: UUID):
        return self.db.execute(
            text("""
                SELECT team_id, user_id, membership_role, created_at
                FROM public.team_members
                WHERE team_id = :team_id
                ORDER BY created_at ASC
            """),
            {"team_id": str(team_id)},
        ).mappings().all()
