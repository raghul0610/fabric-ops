# Day 06 — Frontend Integration + Role-Based UX

## Goal

Connect the working FastAPI/Supabase backend to a real React + TypeScript frontend without moving authorization into the browser.

## Implemented

- Vite + React + TypeScript frontend under `frontend/`.
- Tailwind CSS v3 styling and reusable UI primitives.
- Supabase Auth sign-in/sign-out and session bootstrap.
- API client that attaches the current Supabase access token.
- Role-aware navigation for ADMIN, LEAD and MEMBER.
- Event, team, task, submission and review screens wired to the existing API.
- ADMIN event/team/task creation controls.
- LEAD team/task management and submission review controls.
- MEMBER assigned-task execution and submission flow.
- FastAPI CORS configuration for the local frontend origin.
- Frontend environment configuration uses only the Supabase publishable key.

## Security boundary

The frontend only controls usability. The backend remains authoritative for authentication, role checks, team membership and state transitions. No service-role Supabase key is used in the browser.

## Acceptance

- A Supabase Auth user can sign in from the frontend.
- The frontend obtains the application role from `/events/me`.
- API requests carry the authenticated bearer token.
- Role-specific controls are visible only where useful, while backend authorization remains authoritative.
- Event → team → task → submission → review is navigable from the UI.
- The frontend is buildable with `npm run build`.
