"""Environment configuration for CareerChat.

Auto-detects three modes:
1. Foundry SDK (palantir_models available) — internal auth, no API key needed
2. Vantage/Foundry proxy — OpenAI-compatible REST proxy with FOUNDRY_TOKEN
3. Direct OpenAI — local dev with OPENAI_API_KEY
"""
import os

FOUNDRY_URL: str | None = os.environ.get("FOUNDRY_URL")
FOUNDRY_TOKEN: str | None = os.environ.get("FOUNDRY_TOKEN")
OPENAI_API_KEY: str | None = os.environ.get("OPENAI_API_KEY")
MODEL_NAME: str = os.environ.get("MODEL_NAME", "gpt-5.1")
IS_VANTAGE: bool = bool(FOUNDRY_URL)

try:
    import palantir_models  # noqa: F401
    IS_FOUNDRY_SDK: bool = True
except ImportError:
    IS_FOUNDRY_SDK: bool = False
