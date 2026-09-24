"""Provider-specific implementation for the OpenAI SDK."""

from typing import Any, Protocol


class LLMProvider(Protocol):
    def generate(self, messages: list[dict[str, str]], system_prompt: str) -> str:
        """Return one assistant response for the supplied conversation."""


class ProviderError(RuntimeError):
    """Raised when an LLM provider cannot produce a usable response."""


class OpenAIProvider:
    """Thin adapter around the official OpenAI Python SDK."""

    def __init__(self, api_key: str, model: str, client: Any | None = None) -> None:
        self._model = model
        if client is not None:
            self._client = client
            return
        try:
            from openai import OpenAI
        except ImportError as error:
            raise ProviderError("The openai package is not installed. Run: pip install -r requirements.txt") from error
        self._client = OpenAI(api_key=api_key)

    def generate(self, messages: list[dict[str, str]], system_prompt: str) -> str:
        try:
            response = self._client.responses.create(
                model=self._model, instructions=system_prompt, input=messages
            )
        except Exception as error:
            raise ProviderError("The LLM request failed. Check your connection and settings.") from error

        text = str(getattr(response, "output_text", "")).strip()
        if not text:
            raise ProviderError("The LLM returned an empty response.")
        return text
