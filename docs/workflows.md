# V1 Workflows

## Event workflow

DRAFT → PLANNED → ACTIVE → COMPLETED

Cancellation:
PLANNED → CANCELLED
ACTIVE → CANCELLED

Invalid examples:
- DRAFT → ACTIVE
- COMPLETED → ACTIVE
- CANCELLED → ACTIVE

## Task workflow

TODO → IN_PROGRESS → SUBMITTED → APPROVED

Rework:
SUBMITTED → REJECTED → IN_PROGRESS

Invalid examples:
- TODO → APPROVED
- IN_PROGRESS → APPROVED
- APPROVED → IN_PROGRESS
- REJECTED → APPROVED without a new submission

## Operational journey

Setup:
ADMIN/LEAD creates event → creates team → adds member → creates task → assigns task.

Execution:
MEMBER views assigned task → starts task → performs work → submits.

Review:
Reviewer reads submission → approves or rejects.

Rework:
If rejected, task returns to IN_PROGRESS → member updates work → submits again.

Audit:
Important mutations record actor, action, target, and time.

## Authorization principle

Every protected mutation evaluates:
1. authenticated identity
2. application role
3. event/team membership or administrative scope
4. target resource scope
5. domain state transition rules
