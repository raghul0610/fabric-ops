# Day 05 — Submission, Review, Audit + Hardening

## Goal
Complete the operational loop and harden it.

## Submission
A submission belongs to one task and records the submitter, content/reference, and creation time. Only the assigned member can submit an `IN_PROGRESS` task. Creating a submission moves the task to `SUBMITTED`.

## Review
A review belongs to a submission and records the reviewer, decision, optional feedback, and creation time. Only ADMIN or an authorized LEAD can review, and the reviewer must differ from the submitter.

`APPROVED` moves the task to `APPROVED`. `REJECTED` moves it to `REJECTED`; the existing Day 4 workflow then allows rework through `IN_PROGRESS`.

## Audit
Submission creation and review decisions create append-oriented audit records containing actor, action, entity type, entity id, metadata, and timestamp.

## Database
`submissions`, `reviews`, and `audit_logs` are created with foreign keys, indexes, and RLS. The schema is represented by the Day 5 Alembic migration.

## Acceptance
- Submission authorization is enforced server-side.
- Review authorization is enforced server-side.
- Invalid task states cannot be submitted or reviewed.
- Reviewer cannot be the submitter.
- Submission/review mutations create audit records.
- Service-layer tests cover authorization and state behavior.
