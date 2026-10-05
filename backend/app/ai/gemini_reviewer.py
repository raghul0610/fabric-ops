from google import genai
from google.genai import types

from app.ai.reviewer import AiReviewResult, SubmissionReviewInput


class GeminiSubmissionReviewer:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def review(self, payload: SubmissionReviewInput) -> AiReviewResult:
        prompt = f"""
Evaluate a technical task submission against the task requirements.

Task title:
{payload.task_title}

Task description:
{payload.task_description or "No description provided."}

Submission:
{payload.submission_content}

Return a concise, evidence-based evaluation.
Do not make a final human approval decision. Use REVIEW when the evidence is insufficient.
""".strip()

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an evaluation assistant for FABRIC Ops. "
                    "Evaluate submissions objectively against their task requirements."
                ),
                response_mime_type="application/json",
                response_schema=AiReviewResult,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty review payload")

        return AiReviewResult.model_validate_json(response.text)
