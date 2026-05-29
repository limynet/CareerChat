from src.ai.client import get_client, get_model_name
from src.ai.prompts import EXTRACTION_PROMPT, CANDIDATE_QA_PROMPT, COMPARE_RANK_PROMPT
from src.ai.extractor import extract_candidate, chat_about_candidate, compare_candidates

__all__ = [
    "get_client",
    "get_model_name",
    "EXTRACTION_PROMPT",
    "CANDIDATE_QA_PROMPT",
    "COMPARE_RANK_PROMPT",
    "extract_candidate",
    "chat_about_candidate",
    "compare_candidates",
]
