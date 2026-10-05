# Day 08 — AI Evaluation Foundation

## Goal

Introduce AI as a bounded backend capability without changing the existing workflow authority.

## Implemented

- Added a provider-independent submission reviewer interface.
- Added a Gemini API adapter using the official Google GenAI Python SDK.
- Added structured JSON output validation with Pydantic.
- Added a reviewer-only endpoint:
  POST /submissions/{submission_id}/ai-review
- LEAD access remains limited to their team.
- MEMBER users cannot request AI reviews.
- AI does not approve or reject tasks in the database.
- Missing AI configuration returns 503 instead of failing application startup.
- Added service-level tests using a fake reviewer, so CI does not require an API key.

## Architecture

Submission -> FastAPI authorization -> AiReviewService -> SubmissionReviewer -> Gemini

The reviewer is an interface, so the provider can be replaced without changing domain logic.

## Environment

Add these variables to the backend environment when enabling the provider:

GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.8-flash

The API key must remain backend-only.

## Acceptance

A reviewer can request an AI evaluation for a submitted task, receive a validated recommendation, and still make the final human approval/rejection decision through the existing review workflow.


## Day 09 — Persistence and reviewer UI

### Implemented
- Added `public.ai_evaluations` to persist every AI evaluation.
- Stored submission, requester, model, score, recommendation, summary, strengths, issues, and creation time.
- Added reviewer-only GET endpoint:
  `GET /submissions/{submission_id}/ai-reviews`
- AI review requests now persist their validated result transactionally.
- Added reviewer UI to run an AI evaluation and inspect the latest persisted result.
- Added a "Run again" path that creates a new immutable evaluation instead of overwriting history.
- Human APPROVED/REJECTED review remains the authoritative workflow decision.

### Acceptance
A LEAD or ADMIN can evaluate a SUBMITTED task, see the persisted AI result in the Reviews view, run another evaluation when needed, and then independently approve or reject the submission.
