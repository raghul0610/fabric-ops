# FABRIC Ops V1 Workflows

## Event Lifecycle
DRAFT → PLANNED → ACTIVE → COMPLETED
PLANNED → CANCELLED
ACTIVE → CANCELLED

## Task Lifecycle
TODO → IN_PROGRESS → SUBMITTED
SUBMITTED → APPROVED
SUBMITTED → REJECTED → IN_PROGRESS

## Permissions
ADMIN: full event/team/task administration, member assignment, submission review, audit access.

LEAD: manage permitted event/team work, create/assign tasks in scope, review submissions in scope, view relevant history.

MEMBER: view permitted teams, view assigned tasks, update working states, submit work, view own submission status.

## Critical Journey
ADMIN/LEAD creates event → creates team → adds member → creates task
→ MEMBER views task → starts → submits
→ REVIEWER approves or rejects
→ important transitions are written to audit history.

## Audit Events
event.created
event.status_changed
team.created
member.added
task.created
task.assigned
task.status_changed
submission.created
submission.approved
submission.rejected
