"""day 02 core schema"""
from alembic import op

revision = "20261004_day02"
down_revision = None
branch_labels = None
depends_on = None

SQL = """
create extension if not exists pgcrypto;

create type public.app_role as enum ('ADMIN', 'LEAD', 'MEMBER');
create type public.event_state as enum ('DRAFT', 'PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED');
create type public.task_state as enum ('TODO', 'IN_PROGRESS', 'SUBMITTED', 'APPROVED', 'REJECTED');

create table public.users (
  id uuid primary key references auth.users(id) on delete cascade,
  role public.app_role not null default 'MEMBER',
  created_at timestamptz not null default now()
);

create table public.events (
  id uuid primary key default gen_random_uuid(),
  name text not null check (length(trim(name)) > 0),
  description text,
  state public.event_state not null default 'DRAFT',
  starts_at timestamptz,
  ends_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (ends_at is null or starts_at is null or ends_at > starts_at)
);

create table public.teams (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id) on delete cascade,
  name text not null check (length(trim(name)) > 0),
  created_at timestamptz not null default now(),
  unique (id, event_id),
  unique (event_id, name)
);

create table public.team_members (
  team_id uuid not null references public.teams(id) on delete cascade,
  user_id uuid not null references public.users(id) on delete cascade,
  membership_role public.app_role not null default 'MEMBER',
  created_at timestamptz not null default now(),
  primary key (team_id, user_id)
);

create table public.tasks (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id) on delete cascade,
  team_id uuid not null,
  title text not null check (length(trim(title)) > 0),
  description text,
  assignee_id uuid,
  state public.task_state not null default 'TODO',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint tasks_team_event_fk foreign key (team_id, event_id)
    references public.teams(id, event_id),
  constraint tasks_assignee_team_fk foreign key (team_id, assignee_id)
    references public.team_members(team_id, user_id)
);

create index idx_teams_event_id on public.teams(event_id);
create index idx_team_members_user_id on public.team_members(user_id);
create index idx_tasks_event_id on public.tasks(event_id);
create index idx_tasks_team_id on public.tasks(team_id);
create index idx_tasks_assignee_id on public.tasks(assignee_id);
create index idx_tasks_state on public.tasks(state);
create index idx_tasks_team_event on public.tasks(team_id, event_id);
create index idx_tasks_assignee_team on public.tasks(assignee_id, team_id);

alter table public.users enable row level security;
alter table public.events enable row level security;
alter table public.teams enable row level security;
alter table public.team_members enable row level security;
alter table public.tasks enable row level security;

create policy "users_select_self" on public.users for select to authenticated
using ((select auth.uid()) = id);
create policy "events_select_authenticated" on public.events for select to authenticated using (true);
create policy "teams_select_authenticated" on public.teams for select to authenticated using (true);
create policy "team_members_select_authenticated" on public.team_members for select to authenticated using (true);
create policy "tasks_select_authenticated" on public.tasks for select to authenticated using (true);

create or replace function public.set_updated_at()
returns trigger language plpgsql set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger events_set_updated_at before update on public.events
for each row execute function public.set_updated_at();
create trigger tasks_set_updated_at before update on public.tasks
for each row execute function public.set_updated_at();
"""

def upgrade() -> None:
    op.execute(SQL)

def downgrade() -> None:
    op.execute("""
    drop table if exists public.tasks cascade;
    drop table if exists public.team_members cascade;
    drop table if exists public.teams cascade;
    drop table if exists public.events cascade;
    drop table if exists public.users cascade;
    drop type if exists public.task_state;
    drop type if exists public.event_state;
    drop type if exists public.app_role;
    """)
