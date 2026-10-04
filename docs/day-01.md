# Day 01 — System Definition

## Objective

Freeze the V1 product contract before application code is implemented.

FABRIC Ops is an internal operations platform for running FABRIC events. It manages the operational chain:

**Event → Team → Task → Submission → Review → Audit**

V1 is a **modular monolith**. We are deliberately not introducing microservices until there is a demonstrated operational reason.

## V1 users

### ADMIN
Organization and event administration.

Can:
- create and manage events
- manage teams and members
- create and assign tasks
- view submissions and review outcomes
- inspect operational history

### LEAD
Operational management within permitted event/team scope.

Can:
- manage permitted team work
- create/manage permitted tasks
- assign work to team members
- review submissions where permitted

### MEMBER
Executes assigned work.

Can:
- view permitted tasks
- move assigned work into progress
- submit completed work
- see the review result

The backend is the authorization boundary. Frontend visibility is not a security control.

## Core entities

- User — authenticated identity and application role
- Event — operational event and its lifecycle
- Team — group participating in an event
- TeamMember — membership and role within a team
- Task — unit of assigned work
- Submission — member's submitted result for a task
- Review — approval/rejection decision
- AuditLog — immutable record of important state-changing actions

## State machines

### Event

`DRAFT → PLANNED → ACTIVE → COMPLETED`

Cancellation:
`PLANNED → CANCELLED`
`ACTIVE → CANCELLED`

Invalid transitions must be rejected by the backend.

### Task

`TODO → IN_PROGRESS → SUBMITTED → APPROVED`

Rejection:
`SUBMITTED → REJECTED → IN_PROGRESS`

A member cannot approve their own submission.

## Critical V1 journey

1. ADMIN/LEAD creates an event.
2. ADMIN/LEAD creates a team.
3. A user is added to the team.
4. ADMIN/LEAD creates a task.
5. The task is assigned to a permitted team member.
6. MEMBER starts and completes the work.
7. MEMBER submits the work.
8. A permitted reviewer approves or rejects it.
9. A rejection returns the task to `IN_PROGRESS`.
10. Important mutations are represented in the audit history.

## Explicit non-goals

V1 does not include:
- AI assistant
- chat
- mobile application
- billing
- microservices
- complex analytics
- generic workflow builder
- external notification infrastructure

## Architecture decision

Frontend: React + TypeScript + Tailwind CSS

Backend: FastAPI

Database: PostgreSQL / Supabase PostgreSQL

Authentication: Supabase Auth

CI: GitHub Actions

Backend structure:

`Router → Service → Repository/Database`

The service layer owns business rules. Routers handle HTTP concerns. Database access is kept behind a clear persistence boundary.

## Day 1 acceptance criteria

Day 1 is complete when:
- V1 scope is explicit.
- Roles and permissions are defined.
- Core entities are identified.
- Event and task state transitions are defined.
- The critical operational journey is defined.
- Architecture boundaries are explicit.
- Out-of-scope features are recorded.
- The design is documented before implementation begins.
