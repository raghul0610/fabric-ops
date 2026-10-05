from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AiReviewResponse(BaseModel):
    id: UUID
    submission_id: UUID
    requested_by: UUID
    model: str
    score: int = Field(ge=0, le=100)
    recommendation: str = Field(pattern="^(APPROVE|REJECT|REVIEW)$")
    summary: str
    strengths: list[str]
    issues: list[str]
    created_at: datetime
