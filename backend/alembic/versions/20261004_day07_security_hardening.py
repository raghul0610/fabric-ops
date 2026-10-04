"""day 07 security hardening"""

from alembic import op


revision = "20261004_day07"
down_revision = "20261004_day05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;

        REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM PUBLIC;
        REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM anon;
        REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM authenticated;
    """)


def downgrade() -> None:
    op.execute("""
        GRANT EXECUTE ON FUNCTION public.rls_auto_enable() TO anon;
        GRANT EXECUTE ON FUNCTION public.rls_auto_enable() TO authenticated;
        ALTER TABLE public.alembic_version DISABLE ROW LEVEL SECURITY;
    """)
