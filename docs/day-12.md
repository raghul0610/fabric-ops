# Day 12 — V1 regression coverage and CI boundaries

Day 12 turns the V1 authorization model into a repeatable regression boundary.

## Implemented

- Expanded the real Supabase V1 workflow with negative authorization checks.
- Verified LEAD and MEMBER cannot read an unrelated event.
- Verified LEAD cannot change the lifecycle of an unrelated event.
- Verified scoped event listings exclude events outside team membership while ADMIN retains global visibility.
- Verified LEAD and MEMBER cannot access teams outside their membership scope.
- Verified MEMBER cannot directly access a task from an unrelated team.
- Verified MEMBER cannot invoke the AI review endpoint.
- Expanded role-boundary unit tests for event, team, team-member, review, and AI-review permissions.
- Changed pull-request CI to run deterministic unit/security tests with `--strict-markers` while excluding the external Supabase integration suite.
- Kept the integration suite explicitly marked so it can be run against the configured FABRIC Supabase environment.

## CI boundary

Pull-request CI must not depend on private Supabase credentials or an external database. The deterministic suite runs with:

```text
pytest -m "not integration" --strict-markers
```

The V1 integration suite remains the acceptance test for a configured environment:

```text
pytest -m integration
```

The integration test skips when the required FABRIC environment variables or external dependencies are unavailable. This keeps local development usable without turning an unavailable external service into a false application failure.

## Acceptance

V1 must satisfy both layers:

1. Deterministic CI: authentication, role boundaries, resource scope, state transitions, transactional behavior, AI validation/rate limiting, and health behavior pass without external services.
2. Configured integration acceptance: ADMIN → LEAD → MEMBER workflow succeeds, while cross-event resource access is denied with 403.

No database migration is required for Day 12.
