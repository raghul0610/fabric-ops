from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.openai_reviewer import OpenAISubmissionReviewer
from app.auth import CurrentUser, require_role
from app.config import get_settings
from app.db import get_db
from app.repositories.submission_repository import SubmissionRepository
from app.schemas.ai_review import AiReviewResponse
from app.services.ai_review_service import AiReviewService


router = APIRouter(tags=["ai"])


def get_ai_review_service(db=Depends(get_db)) -> AiReviewService:
    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI review is not configured",
        )
    return AiReviewService(
        SubmissionRepository(db),
        OpenAISubmissionReviewer(settings.openai_api_key, settings.openai_model),
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
