# Day 02 — Backend + Database Foundation

## Goal
Create the backend foundation and make the first operational domain usable through APIs.

## Implemented
- FastAPI application and health endpoint
- Pydantic Settings configuration
- PostgreSQL connection via SQLAlchemy + psycopg
- Alembic migration
- Supabase Auth integration boundary
- Server-side RBAC dependency
- Users, events, teams, team members, and tasks
- Router → service → database structure
- API validation and error handling
- Initial API tests
- Environment template

## Architecture
Router → Service → Repository/database boundary. Authentication is verified through Supabase Auth; the backend is the authorization boundary.

## First vertical slice
ADMIN/LEAD: create event → create team → add member → create task → assign member.
MEMBER: view permitted tasks.

## Important decisions
- Synchronous SQLAlchemy + psycopg for V1.
- Alembic owns migration history.
- Supabase publishable key only; no service-role key in code.
- Role checks are server-side.
- The migration is committed but no unrelated production Supabase project is modified.

## Acceptance
Health works, protected routes require auth, event/team/task APIs exist, assignment requires team membership, and tests cover the health/auth boundary.

## Not done
Frontend, dashboard, submissions/review UI, CI/CD, production database provisioning.
