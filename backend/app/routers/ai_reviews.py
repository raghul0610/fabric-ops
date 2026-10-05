from uuid import UUID

from fastapi import APIRouter, Depends

from app.ai.gemini_reviewer import GeminiSubmissionReviewer
from app.auth import CurrentUser, require_role
from app.config import get_settings
from app.db import get_db
from app.repositories.audit_repository import AuditRepository
from app.repositories.submission_repository import SubmissionRepository
from app.schemas.ai_review import AiReviewResponse
from app.services.ai_review_service import AiReviewService


router = APIRouter(tags=["ai"])


def get_ai_review_service(db=Depends(get_db)) -> AiReviewService:
    settings = get_settings()
    reviewer = (
        GeminiSubmissionReviewer(
            settings.gemini_api_key,
            settings.gemini_model,
            settings.gemini_timeout_ms,
        )
        if settings.gemini_api_key
        else None
    )

    return AiReviewService(
        SubmissionRepository(db),
        reviewer,
        settings.gemini_model,
        AuditRepository(db),
        settings.ai_review_cooldown_seconds,
    )


@router.post(
    "/submissions/{submission_id}/ai-review",
    response_model=AiReviewResponse,
)
def ai_review_submission(
    submission_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD")),
    service: AiReviewService = Depends(get_ai_review_service),
):
    return service.review_submission(submission_id, user.id, user.role)


@router.get(
    "/submissions/{submission_id}/ai-reviews",
    response_model=list[AiReviewResponse],
)
def list_ai_reviews(
    submission_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD")),
    service: AiReviewService = Depends(get_ai_review_service),
):
    return service.list_evaluations(submission_id, user.id, user.role)
