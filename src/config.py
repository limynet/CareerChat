"""Environment configuration for CareerChat.

Auto-detects Vantage/Foundry proxy mode vs direct OpenAI mode
based on whether FOUNDRY_URL is set.
"""
import os

FOUNDRY_URL: str | None = os.environ.get("FOUNDRY_URL")
FOUNDRY_TOKEN: str | None = os.environ.get("FOUNDRY_TOKEN")
OPENAI_API_KEY: str | None = os.environ.get("OPENAI_API_KEY")
MODEL_NAME: str = os.environ.get("MODEL_NAME", "gpt-5.1")
IS_VANTAGE: bool = bool(FOUNDRY_URL)
