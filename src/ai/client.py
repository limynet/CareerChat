"""AI client — dual-mode OpenAI SDK for Vantage proxy or direct OpenAI."""
import os

from openai import OpenAI


def get_client() -> OpenAI:
    """Return a configured OpenAI client.

    Auto-detects Vantage/Foundry proxy mode (FOUNDRY_URL set) vs
    direct OpenAI mode (FOUNDRY_URL not set).
    """
    foundry_url = os.environ.get("FOUNDRY_URL")
    foundry_token = os.environ.get("FOUNDRY_TOKEN")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if foundry_url:
        base_url = f"{foundry_url.rstrip('/')}/api/v2/llm/proxy/openai/v1"
        return OpenAI(base_url=base_url, api_key=foundry_token or "")
    else:
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not set (required for local dev mode)")
        return OpenAI(api_key=openai_api_key)


def get_model_name() -> str:
    """Return the model name to use."""
    return os.environ.get("MODEL_NAME", "gpt-5.1")
