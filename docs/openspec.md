# OpenSpec — FABRIC Ops V1

## Change intent

Establish the domain contract before implementation.

## Problem

Without a fixed domain contract, frontend and backend code can independently invent roles, states, permissions, and relationships. That causes inconsistent behavior and rewrites.

## Proposed solution

Implement V1 as a modular monolith with:
- Supabase Auth for identity
- FastAPI as API and authorization boundary
- PostgreSQL for persistent domain state
- explicit service-layer business rules
- migration-controlled schema
- automated tests for critical transitions

## Constraints

- No service-role secret in frontend code.
- No frontend-only authorization.
- No microservices in V1.
- No generic workflow engine.
- State transitions are explicit.
- Persistence changes are migration-controlled.

## Success criteria

First vertical slice:

ADMIN/LEAD:
create event → create team → add member → create task → assign member

MEMBER:
view task → start task → submit work

REVIEWER:
review submission → approve/reject

SYSTEM:
record important mutations in audit history

## Next milestone

Day 2 establishes the backend and database foundation against the dedicated FABRIC Supabase project.
