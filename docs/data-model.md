# V1 Data Model

## User
Authenticated application user.

Key data: id, role, created_at.

Authentication identity is owned by Supabase Auth.

## Event
Operational event.

Key data: id, name, description, state, starts_at, ends_at, created_at, updated_at.

## Team
Belongs to one event.

Key data: id, event_id, name, created_at.

## TeamMember
Associates a user with a team.

Key data: team_id, user_id, membership_role, created_at.

A user/team pair must be unique.

## Task
Unit of operational work.

Key data: id, event_id, team_id, title, description, assignee_id, state, created_at, updated_at.

The assignee must belong to the task's team.

## Submission
Work submitted for a task.

Key data: id, task_id, submitted_by, content/reference, created_at.

## Review
Review decision for a submission.

Key data: id, submission_id, reviewer_id, decision, feedback, created_at.

The reviewer must be authorized and must differ from the submitter.

## AuditLog
Important domain mutation record.

Key data: id, actor_id, action, entity_type, entity_id, metadata, created_at.

Audit history is append-oriented and not ordinary mutable business state.

## Relationships

Event 1 → N Teams

Team N ↔ N Users through TeamMember

Event 1 → N Tasks

Team 1 → N Tasks

User 1 → N assigned Tasks

Task 1 → N Submissions

Submission 1 → N Reviews

User 1 → N AuditLogs

## Integrity rules

- Team belongs to an existing event.
- Task belongs to the same event as its team.
- Assignee belongs to the task's team.
- Submission references an existing task.
- Review references an existing submission.
- Reviewer is authorized for the task/event.
- Reviewer differs from submitter.
