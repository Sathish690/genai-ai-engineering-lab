"""The only OpenAI SDK integration points."""

from typing import Any, Protocol


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class AnswerGenerator(Protocol):
    def answer(self, prompt: str) -> str: ...


class ProviderError(RuntimeError):
    pass


class OpenAIEmbedder:
    def __init__(self, api_key: str, model: str, client: Any | None = None) -> None:
        self._model = model
        if client is None:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
            except ImportError as error:
                raise ProviderError("The openai package is not installed. Run: pip install -r requirements.txt") from error
        self._client = client

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self._client.embeddings.create(model=self._model, input=texts)
            return [item.embedding for item in response.data]
        except Exception as error:
            raise ProviderError("Embedding request failed.") from error


class OpenAIAnswerGenerator:
    def __init__(self, api_key: str, model: str, client: Any | None = None) -> None:
        self._model = model
        if client is None:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
            except ImportError as error:
                raise ProviderError("The openai package is not installed. Run: pip install -r requirements.txt") from error
        self._client = client

    def answer(self, prompt: str) -> str:
        try:
            response = self._client.responses.create(model=self._model, input=prompt)
            text = response.output_text.strip()
        except Exception as error:
            raise ProviderError("Answer generation request failed.") from error
        if not text:
            raise ProviderError("The LLM returned an empty answer.")
        return text
