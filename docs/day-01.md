# Day 01 — System Definition

## Goal
Define exactly what FABRIC Ops V1 is before implementation starts.

## What we decided
FABRIC Ops is an operational system for events, teams, tasks, submissions, approvals, and audit history. V1 is a modular monolith.

## Roles
- ADMIN: organization/event administration.
- LEAD: manages permitted team/event work.
- MEMBER: executes assigned work and submits it.

## Core workflow
Event → Team → Task → Submission → Review → Audit

Task: TODO → IN_PROGRESS → SUBMITTED → APPROVED; SUBMITTED → REJECTED → IN_PROGRESS.

Event: DRAFT → PLANNED → ACTIVE → COMPLETED; PLANNED/ACTIVE → CANCELLED.

## Deliverables
requirements, architecture, data-model, workflows, and OpenSpec documents.

## Acceptance
The V1 scope, entities, permissions, state transitions, and critical journey are defined before coding.
