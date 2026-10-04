# V1 Requirements

## Functional requirements

### Authentication
- Users authenticate through Supabase Auth.
- Every protected API request requires an authenticated identity.
- Application role is evaluated server-side.

### Authorization
- ADMIN has organization/event administration permissions.
- LEAD is restricted to permitted event/team scope.
- MEMBER can operate only on permitted work.
- A user cannot approve their own submission.
- Unauthorized operations are rejected by the backend.

### Events
- Create and view permitted events.
- Update event metadata.
- Transition events only through valid lifecycle states.

### Teams
- Create a team within an event.
- Add/remove team members.
- Enforce event/team scope.

### Tasks
- Create a task within an event/team.
- Assign only to an eligible team member.
- View permitted tasks.
- Enforce valid task transitions.

### Submissions and reviews
- A permitted member can submit work for an assigned task.
- A permitted reviewer can approve or reject a submission.
- Rejection returns the task to IN_PROGRESS.
- Review decisions are attributable to an authenticated user.

### Audit
- Record important state-changing operations.
- Store actor, action, target, and timestamp.
- Audit records are append-oriented.

## Non-functional requirements

- Backend authorization is authoritative.
- Secrets are never committed.
- Supabase service-role credentials are never exposed to the browser.
- API input is validated.
- Database changes are migration-controlled.
- Critical business rules have automated tests.
- Frontend, API, and persistence concerns remain separable.
- V1 remains deployable as one application.

## Acceptance

A feature is complete only when its API, authorization, state transition, persistence, error handling, and tests agree with the domain rules.
