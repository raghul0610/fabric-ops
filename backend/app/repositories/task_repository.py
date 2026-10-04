from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def team_exists_in_event(self, team_id: UUID, event_id: UUID) -> bool:
        return self.db.execute(
            text("""
                SELECT 1 FROM public.teams
                WHERE id = :team_id AND event_id = :event_id
            """),
            {"team_id": str(team_id), "event_id": str(event_id)},
        ).first() is not None

    def is_team_member(self, team_id: UUID, user_id: UUID) -> bool:
        return self.db.execute(
            text("""
                SELECT 1 FROM public.team_members
                WHERE team_id = :team_id AND user_id = :user_id
            """),
            {"team_id": str(team_id), "user_id": str(user_id)},
        ).first() is not None

    def create(self, *, event_id, team_id, title, description, assignee_id):
        row = self.db.execute(
            text("""
                INSERT INTO public.tasks
                    (event_id, team_id, title, description, assignee_id)
                VALUES
                    (:event_id, :team_id, :title, :description, :assignee_id)
                RETURNING id, event_id, team_id, title, description,
                          assignee_id, state, created_at, updated_at
            """),
            {
                "event_id": str(event_id),
                "team_id": str(team_id),
                "title": title,
                "description": description,
                "assignee_id": str(assignee_id),
            },
        ).mappings().one()
        self.db.commit()
        return row

    def get(self, task_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, event_id, team_id, title, description,
                       assignee_id, state, created_at, updated_at
                FROM public.tasks
                WHERE id = :task_id
            """),
            {"task_id": str(task_id)},
        ).mappings().first()

    def list_for_team(self, team_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, event_id, team_id, title, description,
                       assignee_id, state, created_at, updated_at
                FROM public.tasks
                WHERE team_id = :team_id
                ORDER BY created_at ASC
            """),
            {"team_id": str(team_id)},
        ).mappings().all()

    def list_for_assignee(self, assignee_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, event_id, team_id, title, description,
                       assignee_id, state, created_at, updated_at
                FROM public.tasks
                WHERE assignee_id = :assignee_id
                ORDER BY created_at ASC
            """),
            {"assignee_id": str(assignee_id)},
        ).mappings().all()

    def update_state(self, task_id: UUID, state: str):
        row = self.db.execute(
            text("""
                UPDATE public.tasks
                SET state = :state, updated_at = now()
                WHERE id = :task_id
                RETURNING id, event_id, team_id, title, description,
                          assignee_id, state, created_at, updated_at
            """),
            {"task_id": str(task_id), "state": state},
        ).mappings().first()
        self.db.commit()
        return row
