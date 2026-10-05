# Day 10 — AI quality, security and testing hardening

Day 10 hardens the V1 AI-assisted submission review without expanding the V1 product scope.

## Implemented

- Bounded task title, task description and submission input sizes before sending content to the AI provider.
- Rejected empty/null-character input.
- Added strict structured-output validation for score, recommendation, summary, strengths and issues.
- Added explicit untrusted-content instructions around task and submission text to reduce prompt-injection impact.
- Added a configurable Gemini request timeout.
- Converted provider failures and malformed provider responses into a controlled 503 response.
- Added persisted per-reviewer/per-submission cooldown protection to reduce accidental or abusive repeated AI calls.
- Added an audit record for every persisted AI evaluation request.
- Exposed persisted evaluation identifiers, model and timestamps through the API response.
- Preserved the V1 rule that AI recommendations are advisory and human review remains authoritative.

## Configuration

- `GEMINI_TIMEOUT_MS` defaults to 30000.
- `AI_REVIEW_COOLDOWN_SECONDS` defaults to 10.

## Security boundary

The backend remains authoritative for:
- ADMIN/LEAD authorization.
- Team-scope authorization for LEAD reviewers.
- SUBMITTED-state requirement.
- Human approval/rejection.

The AI provider never receives tools and never directly changes task state.

## Acceptance

Backend tests cover:
- reviewer-only access
- persisted evaluation history
- rate limiting
- provider failure handling
- oversized input rejection
- invalid AI recommendation rejection
- AI audit creation

Google's Gemini API supports system instructions, structured output with Pydantic schemas, and configurable HTTP timeouts; the implementation uses those SDK capabilities for this reviewer. See the official Gemini API documentation before changing the adapter.
