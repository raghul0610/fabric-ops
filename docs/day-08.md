# Day 08 — AI Evaluation Foundation

## Goal

Introduce AI as a bounded backend capability without changing the existing workflow authority.

## Implemented

- Added a submission-reviewer AI interface.
- Added an OpenAI Responses API adapter.
- Added structured Pydantic validation for AI review results.
- Added a reviewer-only endpoint:
  POST /submissions/{submission_id}/ai-review
- LEAD access remains limited to their team.
- MEMBER users cannot request AI reviews.
- AI does not approve or reject tasks in the database.
- Missing AI configuration returns 503 instead of failing application startup.
- Added service-level tests using a fake reviewer, so CI does not require an API key.

## Architecture

Submission -> FastAPI authorization -> AiReviewService -> SubmissionReviewer -> OpenAI

The reviewer is an interface, so the provider can be replaced without changing domain logic.

## Environment

Add these variables to the backend environment when enabling the provider:

OPENAI_API_KEY=
OPENAI_MODEL=gpt-6-luna

The API key must remain backend-only.

## Acceptance

A reviewer can request an AI evaluation for a submitted task, receive a validated recommendation, and still make the final human approval/rejection decision through the existing review workflow.
