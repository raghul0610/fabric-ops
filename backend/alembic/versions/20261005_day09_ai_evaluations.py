"""day 09 persist AI evaluations"""

from alembic import op


revision = "20261005_day09_ai"
down_revision = "20261004_day07_perf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.ai_evaluations (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            submission_id uuid NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
            requested_by uuid NOT NULL REFERENCES public.users(id),
            model text NOT NULL,
            score integer NOT NULL CHECK (score BETWEEN 0 AND 100),
            recommendation text NOT NULL CHECK (recommendation IN ('APPROVE', 'REJECT', 'REVIEW')),
            summary text NOT NULL,
            strengths jsonb NOT NULL DEFAULT '[]'::jsonb,
            issues jsonb NOT NULL DEFAULT '[]'::jsonb,
            created_at timestamptz NOT NULL DEFAULT now()
        );

        CREATE INDEX idx_ai_evaluations_submission_id
            ON public.ai_evaluations(submission_id);
        CREATE INDEX idx_ai_evaluations_requested_by
            ON public.ai_evaluations(requested_by);
        CREATE INDEX idx_ai_evaluations_created_at
            ON public.ai_evaluations(created_at DESC);

        ALTER TABLE public.ai_evaluations ENABLE ROW LEVEL SECURITY;

        CREATE POLICY ai_evaluations_authenticated_select
        ON public.ai_evaluations FOR SELECT TO authenticated USING (true);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.ai_evaluations;")
