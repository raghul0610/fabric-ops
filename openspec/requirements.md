# OpenSpec — FABRIC Ops V1

## Intent
Build one complete operational workflow for events, teams, tasks, submissions, approvals, and audit history.

## Invariants
1. Authentication is required for protected operations.
2. Authorization is enforced server-side.
3. Workflow state transitions are explicit and validated.
4. Important state changes produce audit records.
5. Core foreign-key relationships prevent orphaned records.
6. V1 remains a modular monolith.

## Delivery Order
1. Backend/database foundation
2. Authentication/RBAC
3. Event/team/task workflow
4. Submission/review workflow
5. Audit logging
6. Frontend integration
7. Tests/CI
8. Deployment

## Out of Scope
AI, chat, mobile, billing, microservices, complex analytics, generic workflow configuration.
