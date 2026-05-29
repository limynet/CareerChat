"""Extract structured Candidate data from raw document text using GPT."""
import json
import logging

from openai import OpenAI

from src.ai.client import get_client, get_model_name
from src.ai.prompts import EXTRACTION_PROMPT, CANDIDATE_QA_PROMPT, COMPARE_RANK_PROMPT
from src.models.candidate import Candidate

logger = logging.getLogger(__name__)


def extract_candidate(raw_text: str, filename: str) -> Candidate:
    """Send raw document text to GPT and get back a structured Candidate.

    Args:
        raw_text: Full text extracted from a PDF or DOCX document.
        filename: Original filename of the document.

    Returns:
        Candidate with structured fields extracted by GPT.

    Raises:
        ValueError: If GPT response cannot be parsed as valid Candidate data.
        RuntimeError: If the AI client is not configured.
    """
    client = get_client()
    model = get_model_name()

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": f"Extract candidate data from this document:\n\n{raw_text}"},
        ],
        temperature=0.1,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("GPT returned empty response")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"GPT response is not valid JSON: {e}") from e

    data["raw_text"] = raw_text
    data["source_file"] = filename

    return Candidate.model_validate(data)


def chat_about_candidate(
    candidate: Candidate, question: str, history: list[dict] | None = None
) -> str:
    """Answer a question about a specific candidate using GPT.

    Args:
        candidate: The candidate to discuss.
        question: User's question about the candidate.
        history: Previous chat messages as list of {"role": ..., "content": ...}.

    Returns:
        AI response string.
    """
    client = get_client()
    model = get_model_name()

    candidate_context = f"Candidate data:\n{candidate.model_dump_json(indent=2)}"
    messages = [
        {"role": "system", "content": CANDIDATE_QA_PROMPT},
        {"role": "system", "content": candidate_context},
    ]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content or "No response generated."


def compare_candidates(candidates: list[Candidate], criteria: str = "") -> str:
    """Compare and rank multiple candidates using GPT.

    Args:
        candidates: List of candidates to compare (minimum 2).
        criteria: Optional criteria or role description to rank against.

    Returns:
        AI-generated comparison and ranking analysis.

    Raises:
        ValueError: If fewer than 2 candidates provided.
    """
    if len(candidates) < 2:
        raise ValueError("Need at least 2 candidates to compare")

    client = get_client()
    model = get_model_name()

    summaries = []
    for i, c in enumerate(candidates, 1):
        summaries.append(f"Candidate {i} ({c.name}):\n{c.model_dump_json(indent=2)}")

    all_candidates_text = "\n\n---\n\n".join(summaries)
    user_message = f"Compare these candidates:\n\n{all_candidates_text}"
    if criteria:
        user_message += f"\n\nRanking criteria / role requirements: {criteria}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": COMPARE_RANK_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content or "No comparison generated."
