from pydantic import BaseModel, Field


class AiReviewResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    recommendation: str = Field(pattern="^(APPROVE|REJECT|REVIEW)$")
    summary: str
    strengths: list[str]
    issues: list[str]
