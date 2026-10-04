# FABRIC Ops

FABRIC Operations Platform is a focused internal system for managing event operations, team work, submissions, approvals, and operational history.

## V1 Goal

Support one complete operational workflow:

Admin/Lead creates an event and task → assigns work → member executes and submits → reviewer approves/rejects → every important transition is auditable.

## Scope

### In scope
- Authentication
- Role-based access
- Event management
- Team management
- Task assignment and tracking
- Submission and review workflow
- Audit log
- Basic operational dashboard
- Automated tests
- CI checks

### Explicitly out of scope for V1
- Chat
- AI assistant
- Mobile application
- Billing
- Microservices
- Complex analytics
- Generic workflow builder
- External notification infrastructure

## Roles

- **ADMIN**: controls organization-level operations.
- **LEAD**: manages assigned event/team work and reviews submissions where permitted.
- **MEMBER**: executes assigned tasks and submits work.

Exact permission boundaries will be enforced in the backend, not only in the UI.

## Core Workflow

```
Event
  ↓
Team
  ↓
Task assignment
  ↓
TODO → IN_PROGRESS → SUBMITTED
                         ├──→ APPROVED
                         └──→ REJECTED → IN_PROGRESS
```

Important state changes produce an audit log entry.

## Planned Stack

- Frontend: React + TypeScript + Tailwind CSS
- Backend: FastAPI
- Database: PostgreSQL
- Authentication: Supabase Auth
- CI/CD: GitHub Actions

## Repository Structure

```
frontend/
backend/
docs/
openspec/
tests/
.github/workflows/
```

See:
- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Data Model](docs/data-model.md)
- [Workflows](docs/workflows.md)
