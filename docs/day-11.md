# Day 11 — Authorization scope hardening

Day 11 closes an authorization gap in the V1 event boundary.

## Problem

The API required authentication for event reads, but a non-admin user could request an arbitrary event by ID, and a LEAD could attempt to change the lifecycle of an event outside their team scope.

Authentication alone is not sufficient. The backend must verify that the actor is authorized for the specific resource.

## Implemented

- ADMIN can list and access all events.
- LEAD and MEMBER can list only events connected to teams they belong to.
- LEAD and MEMBER cannot read an unrelated event by ID.
- LEAD can change an event lifecycle only when they belong to a team in that event.
- ADMIN retains global event lifecycle permissions.
- Event scope checks live in the service layer and repository, not only in the router.
- Added tests for global admin access, scoped member listing, unrelated-event denial, and lead lifecycle authorization.

## V1 authorization rule

For resource reads and mutations:

"authenticated" does not imply "authorized".

The backend checks both:
1. identity/role
2. resource scope

No frontend-only control is relied upon for security.

## Acceptance

A user outside an event's team scope must receive 403 for direct event access and scoped lifecycle mutation, while an authorized LEAD and ADMIN retain their permitted operations.
