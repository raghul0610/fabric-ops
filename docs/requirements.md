# FABRIC Ops V1 Requirements

## Objective
Create a single source of truth for FABRIC operational work so event work can be assigned, executed, reviewed, and audited without fragmented manual tracking.

## Functional Requirements
- Authentication is required for protected resources.
- Authorization is enforced server-side.
- Authorized users can create/update events and teams.
- Teams belong to an event in V1.
- Authorized users can create and assign tasks.
- Tasks have priority, deadline, assignee, and lifecycle state.
- Members can access tasks assigned to them.
- Members can submit eligible work.
- Reviewers can approve or reject submissions.
- Rejected submissions can return to in-progress.
- Important mutations create audit records.

## Non-Functional Requirements
- Server-side RBAC
- Input validation
- Database constraints
- No secrets in the repository
- Deterministic workflow transitions
- Explicit API errors
- Transactional consistency for multi-record state changes
- Modular backend structure
- Small frontend components
- Automated CI checks

## V1 Success Criteria
1. Admin/lead creates an event.
2. Team is created.
3. Member is added.
4. Task is assigned.
5. Member starts and submits it.
6. Reviewer approves/rejects.
7. Important actions are visible in audit history.
