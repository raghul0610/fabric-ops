"""day 07 performance FK index"""

from alembic import op

revision = "20261004_day07_perf"
down_revision = "20261004_day07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_tasks_team_assignee "
        "ON public.tasks (team_id, assignee_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS public.idx_tasks_team_assignee")
