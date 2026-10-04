"""day 05 submissions reviews audit"""

from alembic import op


revision = "20261004_day05"
down_revision = "20261004_day02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.submissions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            task_id uuid NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
            submitted_by uuid NOT NULL REFERENCES public.users(id),
            content text NOT NULL CHECK (length(trim(content)) > 0),
            created_at timestamptz NOT NULL DEFAULT now()
        );

        CREATE TABLE public.reviews (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            submission_id uuid NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
            reviewer_id uuid NOT NULL REFERENCES public.users(id),
            decision text NOT NULL CHECK (decision IN ('APPROVED', 'REJECTED')),
            feedback text,
            created_at timestamptz NOT NULL DEFAULT now()
        );

        CREATE TABLE public.audit_logs (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            actor_id uuid NOT NULL REFERENCES public.users(id),
            action text NOT NULL,
            entity_type text NOT NULL,
            entity_id uuid NOT NULL,
            metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
            created_at timestamptz NOT NULL DEFAULT now()
        );

        CREATE INDEX idx_submissions_task_id ON public.submissions(task_id);
        CREATE INDEX idx_submissions_submitted_by ON public.submissions(submitted_by);
        CREATE INDEX idx_reviews_submission_id ON public.reviews(submission_id);
        CREATE INDEX idx_reviews_reviewer_id ON public.reviews(reviewer_id);
        CREATE INDEX idx_audit_logs_entity ON public.audit_logs(entity_type, entity_id);
        CREATE INDEX idx_audit_logs_actor_id ON public.audit_logs(actor_id);

        ALTER TABLE public.submissions ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

        CREATE POLICY submissions_authenticated_select
        ON public.submissions FOR SELECT TO authenticated USING (true);

        CREATE POLICY reviews_authenticated_select
        ON public.reviews FOR SELECT TO authenticated USING (true);

        CREATE POLICY audit_logs_authenticated_select
        ON public.audit_logs FOR SELECT TO authenticated USING (true);
    """)


def downgrade() -> None:
    op.execute("""
        DROP TABLE IF EXISTS public.audit_logs;
        DROP TABLE IF EXISTS public.reviews;
        DROP TABLE IF EXISTS public.submissions;
    """)
