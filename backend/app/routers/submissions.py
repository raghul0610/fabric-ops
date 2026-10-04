from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth import CurrentUser, require_role
from app.db import get_db
from app.repositories.audit_repository import AuditRepository
from app.repositories.submission_repository import SubmissionRepository
from app.schemas.submission import (
    ReviewCreate,
    ReviewResponse,
    SubmissionCreate,
    SubmissionResponse,
)
from app.services.submission_service import SubmissionService


router = APIRouter(tags=["submissions"])


def get_submission_service(db=Depends(get_db)) -> SubmissionService:
    return SubmissionService(SubmissionRepository(db), AuditRepository(db))


@router.post(
    "/tasks/{task_id}/submissions",
    response_model=SubmissionResponse,
    status_code=201,
)
def create_submission(
    task_id: UUID,
    payload: SubmissionCreate,
    user: CurrentUser = Depends(require_role("MEMBER")),
    service: SubmissionService = Depends(get_submission_service),
):
    return service.create(task_id, user.id, payload.content)


@router.get(
    "/tasks/{task_id}/submissions",
    response_model=list[SubmissionResponse],
)
def list_submissions(
    task_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: SubmissionService = Depends(get_submission_service),
):
    return service.list_for_task(task_id, user.id, user.role)


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: UUID,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
    service: SubmissionService = Depends(get_submission_service),
):
    return service.get(submission_id, user.id, user.role)


@router.post(
    "/submissions/{submission_id}/reviews",
    response_model=ReviewResponse,
    status_code=201,
)
def review_submission(
    submission_id: UUID,
    payload: ReviewCreate,
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD")),
    service: SubmissionService = Depends(get_submission_service),
):
    return service.review(
        submission_id,
        user.id,
        user.role,
        payload.decision,
        payload.feedback,
    )
