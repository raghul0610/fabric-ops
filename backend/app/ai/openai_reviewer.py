import json

from openai import OpenAI
from pydantic import ValidationError

from app.ai.reviewer import AiReviewResult, SubmissionReviewInput


class OpenAISubmissionReviewer:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def review(self, payload: SubmissionReviewInput) -> AiReviewResult:
        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "You are an evaluation assistant for a technical event operations platform. "
                "Evaluate a submitted task against its task title and description. "
                "Return JSON only with exactly these fields: score, recommendation, summary, "
                "strengths, issues. score is an integer from 0 to 100. recommendation must be "
                "APPROVE, REJECT, or REVIEW. Do not make the final human approval decision; "
                "REVIEW is preferred when evidence is insufficient. Be concise and evidence-based."
            ),
            input=json.dumps(
                {
                    "task_title": payload.task_title,
                    "task_description": payload.task_description,
                    "submission": payload.submission_content,
                },
                ensure_ascii=False,
            ),
        )

        try:
            return AiReviewResult.model_validate_json(response.output_text)
        except (ValidationError, ValueError) as exc:
            raise RuntimeError("AI provider returned an invalid review payload") from exc
