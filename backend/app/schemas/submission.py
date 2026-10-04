from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SubmissionCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    submitted_by: UUID
    content: str
    created_at: datetime


class ReviewCreate(BaseModel):
    decision: str = Field(pattern="^(APPROVED|REJECTED)$")
    feedback: str | None = Field(default=None, max_length=5000)


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    submission_id: UUID
    reviewer_id: UUID
    decision: str
    feedback: str | None
    created_at: datetime


class SubmissionDetailResponse(SubmissionResponse):
    reviews: list[ReviewResponse]