from typing import Annotated, Literal, Protocol

from pydantic import BaseModel, Field, field_validator


MAX_TASK_TITLE_LENGTH = 200
MAX_TASK_DESCRIPTION_LENGTH = 4000
MAX_SUBMISSION_CONTENT_LENGTH = 12000
MAX_REVIEW_ITEM_LENGTH = 500


class AiReviewProviderError(RuntimeError):
    """Raised when the AI provider fails or returns an invalid response."""


class SubmissionReviewInput(BaseModel):
    task_title: str = Field(min_length=1, max_length=MAX_TASK_TITLE_LENGTH)
    task_description: str | None = Field(default=None, max_length=MAX_TASK_DESCRIPTION_LENGTH)
    submission_content: str = Field(min_length=1, max_length=MAX_SUBMISSION_CONTENT_LENGTH)

    @field_validator("task_title", "submission_content")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("text must not be empty")
        if "\x00" in value:
            raise ValueError("text contains an invalid null character")
        return value

    @field_validator("task_description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if "\x00" in value:
            raise ValueError("text contains an invalid null character")
        return value or None


class AiReviewResult(BaseModel):
    score: int = Field(ge=0, le=100)
    recommendation: Literal["APPROVE", "REJECT", "REVIEW"]
    summary: str = Field(min_length=1, max_length=2000)
    strengths: list[Annotated[str, Field(min_length=1, max_length=MAX_REVIEW_ITEM_LENGTH)]] = Field(
        default_factory=list,
        max_length=10,
    )
    issues: list[Annotated[str, Field(min_length=1, max_length=MAX_REVIEW_ITEM_LENGTH)]] = Field(
        default_factory=list,
        max_length=10,
    )

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("summary must not be empty")
        return value


class SubmissionReviewer(Protocol):
    def review(self, payload: SubmissionReviewInput) -> AiReviewResult:
        ...
