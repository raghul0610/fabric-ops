from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class SubmissionReviewInput:
    task_title: str
    task_description: str | None
    submission_content: str


class AiReviewResult(BaseModel):
    score: int = Field(ge=0, le=100)
    recommendation: str = Field(pattern="^(APPROVE|REJECT|REVIEW)$")
    summary: str = Field(min_length=1, max_length=2000)
    strengths: list[str] = Field(default_factory=list, max_length=10)
    issues: list[str] = Field(default_factory=list, max_length=10)


class SubmissionReviewer(Protocol):
    def review(self, payload: SubmissionReviewInput) -> AiReviewResult:
        ...
