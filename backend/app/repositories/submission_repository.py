from uuid import UUID
import json

from sqlalchemy import text
from sqlalchemy.orm import Session


class SubmissionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_task(self, task_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, event_id, team_id, assignee_id, state
                FROM public.tasks
                WHERE id = :task_id
            """),
            {"task_id": str(task_id)},
        ).mappings().first()

    def get_task_for_ai(self, task_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, team_id, title, description, state
                FROM public.tasks
                WHERE id = :task_id
            """),
            {"task_id": str(task_id)},
        ).mappings().first()

    def is_team_member(self, team_id: UUID, user_id: UUID) -> bool:
        return self.db.execute(
            text("""
                SELECT 1 FROM public.team_members
                WHERE team_id = :team_id AND user_id = :user_id
            """),
            {"team_id": str(team_id), "user_id": str(user_id)},
        ).first() is not None

    def create(self, task_id: UUID, submitted_by: UUID, content: str):
        return self.db.execute(
            text("""
                INSERT INTO public.submissions (task_id, submitted_by, content)
                VALUES (:task_id, :submitted_by, :content)
                RETURNING id, task_id, submitted_by, content, created_at
            """),
            {
                "task_id": str(task_id),
                "submitted_by": str(submitted_by),
                "content": content,
            },
        ).mappings().one()

    def get(self, submission_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, task_id, submitted_by, content, created_at
                FROM public.submissions
                WHERE id = :submission_id
            """),
            {"submission_id": str(submission_id)},
        ).mappings().first()

    def list_for_task(self, task_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, task_id, submitted_by, content, created_at
                FROM public.submissions
                WHERE task_id = :task_id
                ORDER BY created_at ASC
            """),
            {"task_id": str(task_id)},
        ).mappings().all()

    def set_task_state(self, task_id: UUID, state: str) -> None:
        self.db.execute(
            text("""
                UPDATE public.tasks
                SET state = :state, updated_at = now()
                WHERE id = :task_id
            """),
            {"task_id": str(task_id), "state": state},
        )

    def create_review(
        self,
        submission_id: UUID,
        reviewer_id: UUID,
        decision: str,
        feedback: str | None,
    ):
        return self.db.execute(
            text("""
                INSERT INTO public.reviews
                    (submission_id, reviewer_id, decision, feedback)
                VALUES
                    (:submission_id, :reviewer_id, :decision, :feedback)
                RETURNING id, submission_id, reviewer_id,
                          decision, feedback, created_at
            """),
            {
                "submission_id": str(submission_id),
                "reviewer_id": str(reviewer_id),
                "decision": decision,
                "feedback": feedback,
            },
        ).mappings().one()

    def list_reviews(self, submission_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, submission_id, reviewer_id,
                       decision, feedback, created_at
                FROM public.reviews
                WHERE submission_id = :submission_id
                ORDER BY created_at ASC
            """),
            {"submission_id": str(submission_id)},
        ).mappings().all()

    def create_ai_evaluation(
        self,
        submission_id: UUID,
        requested_by: UUID,
        model: str,
        score: int,
        recommendation: str,
        summary: str,
        strengths: list[str],
        issues: list[str],
    ):
        return self.db.execute(
            text("""
                INSERT INTO public.ai_evaluations
                    (submission_id, requested_by, model, score, recommendation,
                     summary, strengths, issues)
                VALUES
                    (:submission_id, :requested_by, :model, :score, :recommendation,
                     :summary, CAST(:strengths AS jsonb), CAST(:issues AS jsonb))
                RETURNING id, submission_id, requested_by, model, score,
                          recommendation, summary, strengths, issues, created_at
            """),
            {
                "submission_id": str(submission_id),
                "requested_by": str(requested_by),
                "model": model,
                "score": score,
                "recommendation": recommendation,
                "summary": summary,
                "strengths": json.dumps(strengths),
                "issues": json.dumps(issues),
            },
        ).mappings().one()

    def list_ai_evaluations(self, submission_id: UUID):
        return self.db.execute(
            text("""
                SELECT id, submission_id, requested_by, model, score,
                       recommendation, summary, strengths, issues, created_at
                FROM public.ai_evaluations
                WHERE submission_id = :submission_id
                ORDER BY created_at DESC
            """),
            {"submission_id": str(submission_id)},
        ).mappings().all()

    def count_recent_ai_evaluations(
        self,
        submission_id: UUID,
        requested_by: UUID,
        cooldown_seconds: int,
    ) -> int:
        return int(self.db.execute(
            text("""
                SELECT count(*)
                FROM public.ai_evaluations
                WHERE submission_id = :submission_id
                  AND requested_by = :requested_by
                  AND created_at > now() - make_interval(secs => :cooldown_seconds)
            """),
            {
                "submission_id": str(submission_id),
                "requested_by": str(requested_by),
                "cooldown_seconds": cooldown_seconds,
            },
        ).scalar_one())

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
