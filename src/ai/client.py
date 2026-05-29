"""AI client — three-mode OpenAI-compatible interface.

Mode 1: Foundry SDK (palantir_models) — internal auth, no API key needed
Mode 2: Vantage/Foundry proxy — OpenAI-compatible REST proxy with FOUNDRY_TOKEN
Mode 3: Direct OpenAI — local dev with OPENAI_API_KEY
"""
import os
import logging
from typing import Any

from openai import OpenAI

from src.config import IS_FOUNDRY_SDK

logger = logging.getLogger(__name__)

# Model name mapping: OpenAI-style → Foundry SDK style
_FOUNDRY_MODEL_MAP: dict[str, str] = {
    "gpt-5.1": "GPT_5_1",
    "gpt-4.1": "GPT_4_1",
    "gpt-4.1-mini": "GPT_4_1_MINI",
    "gpt-4.1-nano": "GPT_4_1_NANO",
    "o3": "O3",
    "o4-mini": "O4_MINI",
}


def _to_foundry_model(model: str) -> str:
    """Map an OpenAI-style model name to a Foundry SDK model identifier."""
    return _FOUNDRY_MODEL_MAP.get(model, model.upper().replace("-", "_").replace(".", "_"))


def _role_to_foundry(role: str) -> Any:
    """Convert a string role to a ChatMessageRole enum value."""
    from language_model_service_api.languagemodelservice_api import ChatMessageRole

    mapping = {
        "system": ChatMessageRole.SYSTEM,
        "user": ChatMessageRole.USER,
        "assistant": ChatMessageRole.ASSISTANT,
    }
    return mapping.get(role, ChatMessageRole.USER)


class FoundryClient:
    """Adapter that wraps palantir_models to expose the OpenAI SDK interface.

    Provides client.chat.completions.create() identical to the OpenAI SDK,
    so extractor.py works unchanged.
    """

    class _Completions:
        def create(self, *, model: str, messages: list[dict], **kwargs: Any) -> Any:
            from language_model_service_api.languagemodelservice_api_completion_v3 import (
                GptChatCompletionRequest,
            )
            from language_model_service_api.languagemodelservice_api import ChatMessage
            from palantir_models.models import OpenAiGptChatLanguageModel

            # Convert message dicts to ChatMessage objects
            chat_messages = [
                ChatMessage(_role_to_foundry(m["role"]), m["content"])
                for m in messages
            ]

            foundry_model_name = _to_foundry_model(model)
            logger.debug("FoundryClient: requesting model %s (mapped from %s)", foundry_model_name, model)

            llm = OpenAiGptChatLanguageModel.get(foundry_model_name)
            request = GptChatCompletionRequest(chat_messages)
            # response_format and temperature are silently ignored
            return llm.create_chat_completion(request)

    class _Chat:
        def __init__(self) -> None:
            self.completions = FoundryClient._Completions()

    def __init__(self) -> None:
        self.chat = FoundryClient._Chat()


def get_client() -> OpenAI | FoundryClient:
    """Return a configured AI client.

    Three-mode detection:
    1. Foundry SDK (palantir_models importable) → FoundryClient
    2. FOUNDRY_URL set → OpenAI SDK pointed at Foundry proxy
    3. OPENAI_API_KEY set → direct OpenAI SDK
    4. Otherwise → ValueError
    """
    if IS_FOUNDRY_SDK:
        logger.info("Using Foundry SDK mode (palantir_models)")
        return FoundryClient()

    foundry_url = os.environ.get("FOUNDRY_URL")
    foundry_token = os.environ.get("FOUNDRY_TOKEN")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if foundry_url:
        base_url = f"{foundry_url.rstrip('/')}/api/v2/llm/proxy/openai/v1"
        logger.info("Using Foundry proxy mode (%s)", base_url)
        return OpenAI(base_url=base_url, api_key=foundry_token or "")

    if openai_api_key:
        logger.info("Using direct OpenAI mode")
        return OpenAI(api_key=openai_api_key)

    raise ValueError(
        "No AI client configuration found. "
        "Set OPENAI_API_KEY for local dev, FOUNDRY_URL for proxy mode, "
        "or run on Vantage with palantir_models available."
    )


def get_model_name() -> str:
    """Return the model name to use."""
    return os.environ.get("MODEL_NAME", "gpt-5.1")
