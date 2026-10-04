# FABRIC Ops V1 Architecture

## Decision
Use a modular monolith for V1. Microservices are not justified by the current problem size.

## Components

```
React + TypeScript
        │ HTTPS / REST
        ▼
FastAPI Backend
  ├─ authentication integration
  ├─ RBAC
  ├─ domain services
  ├─ workflow transitions
  └─ audit logging
        │
   ┌────┴────┐
   ▼         ▼
PostgreSQL  Supabase Auth
```

## Backend Modules
auth, users, events, teams, tasks, submissions, audit

Domain rules belong in backend service/domain code, not UI components.

## Authorization
The frontend may hide controls for usability, but the backend is the source of truth for permissions.

## State Transitions
Event: DRAFT → PLANNED → ACTIVE → COMPLETED; PLANNED/ACTIVE → CANCELLED

Task: TODO → IN_PROGRESS → SUBMITTED → APPROVED; SUBMITTED → REJECTED → IN_PROGRESS

Invalid transitions return domain errors.

## Consistency
State changes that also write related records/audit events should run in a database transaction.

## Deployment
React frontend + one FastAPI backend + managed PostgreSQL + Supabase Auth.
